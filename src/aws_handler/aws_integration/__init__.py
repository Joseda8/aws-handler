from aws_handler.aws_integration.connectors.boto3.boto3_connector import (
    Boto3Connector,
)

# Instantiate aws_connector and expose it
aws_connector = Boto3Connector()
__all__ = ["aws_connector"]
