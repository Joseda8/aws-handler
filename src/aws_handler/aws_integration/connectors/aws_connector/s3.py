from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


# Interface for AWS S3 connectors
class AwsS3(ABC):
    @abstractmethod
    def s3_list_files(
        self, bucket: str, folder: str = "", keywords: List[str] = None
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Lists objects (files) within an Amazon S3 bucket, optionally filtered by keywords.

        :param bucket: The name of the S3 bucket.
        :param folder: A common folder for all the files to be searched.
        :param keywords: Optional list of keywords to search for files within the bucket.

        :return: A dictionary where each key represents a prefix, and the corresponding value is a list of dictionaries
                 containing "file_path" and "last_modified" for each file.
        """
        pass

    @abstractmethod
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

    def s3_read_file_by_chunks(
        self,
        bucket: str,
        key: str,
        code: str = "utf-8",
        chunk_size: int = 65536,
        bytes_: bool = False,
        raw: bool = False,
    ) -> Optional[Tuple[bytes, str]]:
        """
        Stream a file from an S3 bucket in smaller, manageable chunks.

        :param bucket: S3 bucket name.
        :param key: S3 key (file path) for the file in the S3 bucket.
        :param code: The encoding to use when decoding chunks (default is 'utf-8').
        :param chunk_size: The size of each chunk to read from the S3 object (default is 65536 bytes).
        :param bytes_: If True, yields each chunk as a `BytesIO` stream suitable for pandas (default is False).
        :param raw: If True, yields raw byte data for each chunk (default is False).
        :return: A generator that yields a tuple of (file content chunk, encoding) for each chunk read,
                or None if the object does not exist in S3.
        """
