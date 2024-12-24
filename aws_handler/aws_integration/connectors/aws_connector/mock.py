# flake8: noqa

from typing import Dict, List, Optional, Tuple, Union
import io
import pandas as pd
from aws_handler.aws_integration.connectors.aws_connector import AwsConnector


class AwsConnectorMock(AwsConnector):

    def _verify_aws_connection(self):
        pass

    def s3_list_files(
        self, bucket: str, folder: str = "", keywords: List[str] = None
    ) -> Dict[str, List[Dict[str, str]]]:
        return {}

    def s3_read_file(
        self,
        bucket: str,
        key: str,
        code: str = "utf-8",
        raw: bool = False,
        bytes_: bool = False,
    ) -> Tuple[Optional[bytes], Optional[str]]:
        return None, None

    def s3_read_file_by_chunks(
        self,
        bucket: str,
        key: str,
        code: str = "utf-8",
        chunk_size: int = 65536,
        bytes_: bool = False,
        raw: bool = False,
    ) -> Optional[Tuple[bytes, str]]:
        return None

    def upload_dataframe_to_s3(
        self,
        data: Union[pd.DataFrame, io.BytesIO],
        bucket: str,
        key: str,
        file_format: str,
    ) -> None:
        return None

    def put_object_to_s3(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> None:
        return None

    def put_dict_to_s3(self, bucket: str, key: str, dict_obj: Dict) -> None:
        return None
