from aws_handler import S3Reader, S3Writer
from aws_handler.aws_integration.connectors.aws_connector import (
    AwsConnectorMock,
)

# Common constants
AWS_CONNECTOR = AwsConnectorMock()

TEST_BUCKET = "my-bucket"
TEST_KEYWORD_JSON_FILES = "*.json"
TEST_JSON_FOLDER = "files/json"
TEST_JSON_FILE_NAME = "test.json"
TEST_JSON_DATA = {"hello": "world"}


def test_writer():
    """
    Test the interface of the S3Writer class.

    This test verifies that the S3Writer class can be instantiated with a mock
    AWS connector and checks that it can invoke the 'write_json_to_s3' method
    with the appropriate parameters. This is an interface-level test and does
    not validate the behavior of the method.
    """
    # Create an instance of S3Writer using mock connector
    s3_writer = S3Writer(bucket=TEST_BUCKET, aws_connector=AWS_CONNECTOR)
    s3_writer.write_json_to_s3(
        data=TEST_JSON_DATA,
        file_name=TEST_JSON_FILE_NAME,
        file_path=TEST_JSON_FOLDER,
    )


def test_reader():
    """
    Test the interface of the S3Reader class.

    This test verifies that the S3Reader class can be instantiated with a mock
    AWS connector and checks that it can invoke the 'retrieve_files' method
    with the appropriate parameters. This is an interface-level test and does
    not validate the behavior of the method.
    """
    # Create an instance of S3Reader using mock connector
    s3_reader = S3Reader(bucket=TEST_BUCKET, aws_connector=AWS_CONNECTOR)
    s3_files = s3_reader.retrieve_files(
        path=TEST_JSON_FOLDER, keywords=[TEST_KEYWORD_JSON_FILES]
    )
    assert isinstance(
        s3_files, dict
    ), f"Expected type 'dict', but got {type(s3_files)}"
