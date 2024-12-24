import os

import pandas as pd

from aws_handler.aws_integration import AwsConnector, Boto3Connector
from aws_handler.util.pandas import format_df_to_excel
from aws_handler.util.logger import log


class S3Writer:
    def __init__(self, bucket: str, aws_connector: AwsConnector = None):
        """
        Initialize a S3Writer object.

        :param bucket: The name of the S3 bucket.
        :param aws_connector: AWS connector object used for S3 interactions.
        """
        self._bucket = bucket
        self._aws_connector = (
            aws_connector if aws_connector else Boto3Connector()
        )

    def write_df_to_s3(
        self, df_data: pd.DataFrame, file_name: str, file_path: str
    ):
        """
        Write data to S3 bucket.

        :param df_data: Data to write (already a DataFrame).
        :param file_name: Name of the file to write.
        :param file_path: Path of the file to write.
        """
        if df_data.empty:
            log.debug(f"Attempting to write an empty file: {file_name}")
            return

        # Check file extension to determine file type
        _, extension = os.path.splitext(file_name)
        extension = extension.replace(".", "")
        full_file_path = os.path.join(file_path, file_name)

        # Upload to S3
        if extension == "csv":
            self._aws_connector.upload_dataframe_to_s3(
                data=df_data,
                bucket=self._bucket,
                key=full_file_path,
                file_format=extension,
            )
        elif extension in ["xlsx", "xls"]:
            # Format DataFrame to Excel buffer
            excel_buffer = format_df_to_excel(df_data)
            self._aws_connector.upload_dataframe_to_s3(
                data=excel_buffer,
                bucket=self._bucket,
                key=full_file_path,
                file_format=extension,
            )

    def write_json_to_s3(self, data, file_name: str, file_path: str):
        key = f"{file_path}/{file_name}"
        self._aws_connector.put_dict_to_s3(
            bucket=self._bucket, key=key, dict_obj=data
        )

    def write_txt_to_s3(self, text: str, file_name: str, file_path: str):
        full_file_path = os.path.join(file_path, file_name)
        # Upload to S3
        self._aws_connector.put_object_to_s3(
            bucket=self._bucket,
            key=full_file_path,
            data=text,
            content_type="text/plain",
        )
