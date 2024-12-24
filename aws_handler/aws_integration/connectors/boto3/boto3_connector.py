from typing import Dict, List, Optional, Tuple, Union
import io
import json
import re

import boto3
import botocore
import botocore.client
import pandas as pd

from aws_handler.aws_integration.connectors.aws_connector import AwsConnector
from aws_handler.aws_integration.connectors.boto3.util import (
    detect_encoding_from_bytes,
)
from aws_handler.util.logger import log


class Boto3Connector(AwsConnector):
    # Class variable to store the singleton instance
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the class is created.
        If an instance already exists, return the existing one.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Avoid re-initialization
        if not hasattr(self, "_initialized"):
            # Initialize boto3 client
            self._s3: botocore.client.S3 = None
            # Start AWS connections
            self._verify_aws_connection()
            # Mark as initialized
            self._initialized = True

    def _verify_aws_connection(self):
        try:
            self._s3 = boto3.client("s3")
            log.debug("AWS Connection Verified.")
        except Exception as excpt:
            raise Exception("Failed to verify AWS connection") from excpt

    def s3_list_files(
        self,
        bucket: str,
        folder: str = "",
        keywords: Optional[List[str]] = None,
    ) -> Dict[str, List[Dict[str, str]]]:
        if keywords is None:
            keywords = [""]

        if "" in keywords:
            log.warning(
                "S3 being accessed with no filtering, "
                " this may result in low performance."
            )

        result = {}

        # Get the list of objects with the specified prefix (folder)
        response = self._s3.list_objects_v2(Bucket=bucket, Prefix=folder)

        # Check if the response contains objects
        if "Contents" not in response:
            return result

        result = {}

        # List all objects (files and folders) within the specified folder
        all_objects = [obj_summary for obj_summary in response["Contents"]]

        # Filter out objects that represent folders
        file_objects = [
            obj for obj in all_objects if not obj["Key"].endswith("/")
        ]

        # Create a dictionary using the file path and last_modified
        all_files = [
            {
                "file_path": file["Key"],
                "last_modified": str(file["LastModified"]),
            }
            for file in file_objects
        ]

        # Iterate over each keyword and retrieve the filtered list of files
        for keyword in keywords:
            pattern = keyword.replace("*", ".*")
            filtered_objects = [
                file_path
                for file_path in all_files
                if re.search(pattern, file_path["file_path"])
            ]
            result[keyword] = filtered_objects

        return result

    def s3_read_file(
        self,
        bucket: str,
        key: str,
        code: str = "utf-8",
        raw: bool = False,
        bytes_: bool = False,
    ) -> Tuple[Optional[bytes], Optional[str]]:
        try:
            # Get the file object from S3
            obj = self._s3.get_object(Bucket=bucket, Key=key)["Body"].read()
            encoding = detect_encoding_from_bytes(obj)
        except self._s3.exceptions.NoSuchKey:
            # Handle the case where the object is not found
            return None, None
        except Exception as e:
            # Handle any other unexpected errors
            return None, f"Error: {str(e)}"

        # Return based on the requested format
        if raw:
            return obj, encoding
        elif bytes_:
            return io.BytesIO(obj), encoding
        else:
            return obj.decode(code), encoding

    def s3_read_file_by_chunks(
        self,
        bucket,
        key,
        code="utf-8",
        chunk_size=65536,
        bytes_=False,
        raw=False,
    ):
        try:
            obj = self._s3.get_object(Bucket=bucket, Key=key)["Body"]
            while True:
                chunk = obj.read(chunk_size)
                encoding = detect_encoding_from_bytes(chunk)
                if not chunk:
                    yield -1, -1
                    break
                if raw:
                    yield chunk, encoding
                if bytes_:
                    yield io.BytesIO(chunk), encoding
                else:
                    yield chunk.decode(code), encoding
        except self._s3.exceptions.NoSuchKey:
            return None, None

    def upload_dataframe_to_s3(
        self,
        data: Union[pd.DataFrame, io.BytesIO],
        bucket: str,
        key: str,
        file_format: str,
    ) -> None:
        if isinstance(data, pd.DataFrame):
            # Create BytesIO buffer
            data_buffer = io.BytesIO()
            if file_format == "csv":
                data.to_csv(data_buffer, index=False)
                data_buffer.seek(0)
                self.put_object_to_s3(
                    bucket,
                    key,
                    data_buffer.getvalue(),
                    content_type="text/csv",
                )
            elif file_format in ["excel", "xlsx", "xls"]:
                data.to_excel(data_buffer, index=False, engine="xlsxwriter")
                data_buffer.seek(0)
                self.put_object_to_s3(
                    bucket,
                    key,
                    data_buffer.getvalue(),
                    content_type="application/vnd."
                    "openxmlformats-officedocument."
                    "spreadsheetml.sheet",
                )
            else:
                raise ValueError(
                    "Unsupported file format. "
                    "Only 'csv' and 'excel' are supported."
                )
        elif isinstance(data, io.BytesIO):
            if file_format == "csv":
                self.put_object_to_s3(
                    bucket, key, data.getvalue(), content_type="text/csv"
                )
            elif file_format in ["excel", "xlsx", "xls"]:
                self.put_object_to_s3(
                    bucket,
                    key,
                    data.getvalue(),
                    content_type="application/"
                    "vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet",
                )
            else:
                raise ValueError(
                    "Unsupported file format. "
                    "Only 'csv' and 'excel' are supported."
                )
        else:
            raise ValueError(
                "Unsupported data type. "
                "Expected Pandas DataFrame or BytesIO buffer."
            )

    def put_object_to_s3(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> None:
        self._s3.put_object(
            Body=data, Bucket=bucket, Key=key, ContentType=content_type
        )

    def put_dict_to_s3(self, bucket, key, dict_obj):
        self._s3.put_object(
            Body=json.dumps(dict_obj).encode("utf-8"),
            Bucket=bucket,
            Key=key,
        )
