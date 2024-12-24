from abc import abstractmethod

from .s3 import AwsS3


# Connector class that must implement the methods from AwsS3
class AwsConnector(AwsS3):
    @abstractmethod
    def _verify_aws_connection(self):
        """
        Verify that the connection to AWS is successful.

        This method must be implemented by all subclasses.

        Raises:
            Exception: If the connection cannot be established.
        """
        pass
