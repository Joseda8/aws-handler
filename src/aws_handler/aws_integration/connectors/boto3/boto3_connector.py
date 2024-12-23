from typing import Dict, List, Optional, Tuple
import io
import re

import boto3

from aws_handler.aws_integration.connectors.aws_connector.aws_connector import (
    AwsConnector,
)
from aws_handler.aws_integration.connectors.boto3.util import (
    detect_encoding_from_bytes,
)
from aws_handler.util.logger import log


class Boto3Connector(AwsConnector):

    def __init__(self):
        # Initialize boto3 client once in the constructor
        self._s3 = boto3.client("s3")

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
                "S3 being accessed with no filtering, this may result in low performance."
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

        # Filter out objects that represent folders (objects with trailing slash "/")
        file_objects = [
            obj for obj in all_objects if not obj["Key"].endswith("/")
        ]

        # Create a dictionary using the file path and its last_modified property
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
        """
        Reads a file from S3 and returns its content.

        :param bucket: The S3 bucket name.
        :param key: The S3 object key.
        :param code: The encoding to decode the content (default: 'utf-8').
        :param raw: If True, returns raw bytes.
        :param bytes_: If True, returns an in-memory BytesIO object.
        :return: A tuple of (file content, encoding).
        """
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
