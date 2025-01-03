from typing import Dict, Generator, List, Union

import pandas as pd

from aws_handler.aws_integration import AwsConnector, Boto3Connector
from aws_handler.s3_handler.models import UrlFile, UrlFileCollection
from aws_handler.s3_handler.reader import S3Reader
from aws_handler.s3_handler.writer import S3Writer


class S3Handler:
    def __init__(self, bucket: str, aws_connector: AwsConnector = None):
        """
        Initialize an S3Handler object.

        :param bucket: The name of the S3 bucket.
        :param aws_connector: AWS connector object used for S3 interactions.
        """
        self._bucket = bucket
        self._aws_connector = (
            aws_connector if aws_connector else Boto3Connector()
        )
        self._reader = S3Reader(bucket, self._aws_connector)
        self._writer = S3Writer(bucket, self._aws_connector)

    # S3Writer methods
    def write_df_to_s3(
        self, df_data: pd.DataFrame, file_name: str, file_path: str
    ):
        return self._writer.write_df_to_s3(df_data, file_name, file_path)

    def write_json_to_s3(self, data, file_name: str, file_path: str):
        return self._writer.write_json_to_s3(data, file_name, file_path)

    def write_txt_to_s3(self, text: str, file_name: str, file_path: str):
        return self._writer.write_txt_to_s3(text, file_name, file_path)

    # S3Reader methods
    def retrieve_files(
        self, path: str, keywords: List[str]
    ) -> Dict[str, UrlFileCollection]:
        return self._reader.retrieve_files(path, keywords)

    def read_file(
        self, file_object: UrlFile, custom_encoding: str = ""
    ) -> Union[pd.DataFrame, dict, bytes, None]:
        return self._reader.read_file(file_object, custom_encoding)

    def read_file_by_chunks(
        self, file_object: UrlFile, chunk_size: int = None
    ) -> Generator[pd.DataFrame, None, None]:
        return self._reader.read_file_by_chunks(file_object, chunk_size)
