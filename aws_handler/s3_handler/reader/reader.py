from typing import Dict, Generator, List, Tuple, Union

import csv
import io
import json
import xmltodict

import pandas as pd

from aws_handler.aws_integration import aws_connector
from aws_handler.s3_handler.models import UrlFile, UrlFileCollection


class S3Reader:
    def __init__(self, bucket: str):
        """
        Initialize a S3Reader object.


        :param bucket: The name of the S3 bucket.
        """
        # Init arguments
        self._bucket = bucket

    def retrieve_files(self, path: str, keywords: List[str]):
        """
        Retrieve file information from S3 and store it as UrlFile instances.
        """
        files_per_keyword: Dict[str, UrlFileCollection] = {}
        files_path_per_keyword = aws_connector.s3_list_files(
            bucket=self._bucket, folder=path, keywords=keywords
        )

        # Iterate over each keyword and its files
        for keyword, file_list in files_path_per_keyword.items():
            # Create a new UrlFileCollection instance for each keyword
            url_file_objects = UrlFileCollection()

            # Iterate through each dictionary in the list
            for file_info in file_list:
                # Create a new UrlFile instance
                url_file_obj = UrlFile(
                    s3_url=file_info["file_path"],
                    last_modified=file_info["last_modified"],
                )

                # Append the new UrlFile instance to the list for the current keyword
                url_file_objects.add_url_file_object(url_file_obj)

            # Order files per last_modified property
            url_file_objects.order_files_by_last_modified_or_name()

            # Replace the list of dictionaries with the list of UrlFile instances for the current keyword
            files_per_keyword[keyword] = url_file_objects

        return files_per_keyword

    def _get_decoded_content_first_last_line(
        self, decoded_content: str
    ) -> Tuple[str, str]:
        """
        Get the first and the last lines in a CSV file wrapped in a string.

        :param decoded_content: Content of the CSV file as a string.
        :return: The last and first lines.
        """
        first_line = decoded_content.partition("\n")[0]
        last_line = decoded_content.rpartition("\n")[-1]
        return (first_line, last_line)

    def read_file(
        self, file_object: UrlFile, custom_encoding: str = ""
    ) -> Union[pd.DataFrame, dict, bytes, None]:
        """
        Read a file from S3 based on a UrlFile.

        :param file_object: The UrlFile to be read
        :param custom_encoding: The custom encoding for the file on the S3 bucket. It is an empty string by default.
        :return: The parsed file data
        """
        file_path = file_object.s3_url
        file_type = file_object.file_extension

        if file_type == "json":
            # Read raw content and parse as JSON
            file_content, _ = aws_connector.s3_read_file(
                self._bucket, key=file_path, raw=True
            )
            return json.loads(file_content)
        elif file_type == "csv":
            # Read pandas-ready content, decode, and parse as DataFrame
            file_content, encoding = aws_connector.s3_read_file(
                self._bucket, key=file_path, bytes_=True
            )
            decoded_content = file_content.getvalue().decode(encoding)
            first_line, _ = self._get_decoded_content_first_last_line(
                decoded_content=decoded_content
            )
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(first_line)
            delimiter = dialect.delimiter
            encoding = encoding if custom_encoding == "" else custom_encoding
            df = pd.read_csv(
                file_content, encoding=encoding, engine="python", sep=delimiter
            )
            return df
        elif file_type == "xlsx":
            # Read pandas-ready content, handle single/multiple sheets
            file_content, _ = aws_connector.s3_read_file(
                self._bucket, key=file_path, bytes_=True
            )
            xls = pd.ExcelFile(file_content)
            num_sheets = len(xls.sheet_names)
            if num_sheets == 1:
                df = pd.read_excel(file_content)
            else:
                df = pd.read_excel(file_content, sheet_name=None)
            return df
        elif file_type == "xml":
            # Read non-pandas-ready content and parse as XML
            file_content, _ = aws_connector.s3_read_file(
                self._bucket, key=file_path, bytes_=False
            )
            return xmltodict.parse(file_content)
        elif file_type == "txt":
            # Read raw content
            file_content, encoding = aws_connector.s3_read_file(
                self._bucket, key=file_path, raw=True
            )
            return file_content, encoding
        return None

    def read_file_by_chunks(
        self, file_object: UrlFile, chunk_size: int = None
    ) -> Generator[pd.DataFrame, None, None]:
        """
        Read a file from S3 in chunks and parse it.

        :param file_object: The UrlFile representing the file to be read.
        :param chunk_size: Optional size (in bytes) of each chunk to read at a time.
        :return: A generator yielding parsed chunks.
        """
        file_path = file_object.s3_url
        file_type = file_object.file_extension

        if file_type == "csv":
            # Read the file in chunks from S3, decode, and parse each chunk into a DataFrame
            df_headers = []
            last_line = ""
            for file_content, encoding in aws_connector.s3_read_file_by_chunks(
                bucket=self._bucket,
                chunk_size=chunk_size,
                key=file_path,
                bytes_=True,
            ):
                # If the last chunk is reached, stop processing
                if file_content == -1:
                    break
                # Read chunk
                decoded_content = last_line + file_content.getvalue().decode(
                    encoding
                )
                first_line, last_line = (
                    self._get_decoded_content_first_last_line(
                        decoded_content=decoded_content
                    )
                )
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(first_line)
                delimiter = dialect.delimiter
                file_content_encoded = io.BytesIO(decoded_content.encode())
                df = pd.read_csv(
                    file_content_encoded,
                    encoding=encoding,
                    engine="python",
                    sep=delimiter,
                )
                # Save headers if they were not saved previously, otherwise adjust headers in each new chunk
                if len(df_headers) == 0:
                    df_headers = df.columns.tolist()
                else:
                    # Create a new DataFrame with the current headers as a row
                    df_current_headers = pd.DataFrame(
                        [df.columns.tolist()], columns=df.columns
                    )
                    # Append the new row to the original DataFrame
                    df = pd.concat([df_current_headers, df], ignore_index=True)
                    # Assign correct headers
                    df.columns = df_headers
                # Remove the last row from the DataFrame if it's part of a split row
                if last_line != "":
                    df = df.drop(df.index[-1]) if len(df) > 0 else df
                yield df
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
