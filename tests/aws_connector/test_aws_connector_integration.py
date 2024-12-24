import inspect
import unittest
from aws_handler.aws_integration.connectors.aws_connector import AwsConnector
from aws_handler.aws_integration.connectors.aws_connector import (
    AwsConnectorMock,
)


class TestAwsConnectorInterface(unittest.TestCase):
    """
    Test the interface consistency between AwsConnector
    and AwsConnectorMock classes.

    This test checks that both the AwsConnector and
    AwsConnectorMock classes have the same set of methods
    and that the method signatures match between the
    corresponding methods in both classes.

    This is important because the rest of the tests will work
    with the method AwsConnectorMock.
    """

    def test_aws_connector_interface(self):
        # Get all methods of the classes
        aws_connector_methods = {
            method[0]: method[1]
            for method in inspect.getmembers(
                AwsConnector, predicate=inspect.isfunction
            )
        }
        aws_connector_mock_methods = {
            method[0]: method[1]
            for method in inspect.getmembers(
                AwsConnectorMock, predicate=inspect.isfunction
            )
        }

        # Check if both classes have the same methods
        self.assertEqual(
            set(aws_connector_methods.keys()),
            set(aws_connector_mock_methods.keys()),
            "The methods in AwsConnector and AwsConnectorMock do not match.",
        )

        # Compare the method signatures for each method
        for method_name, method in aws_connector_methods.items():
            # Get the signatures for both classes
            aws_connector_signature = inspect.signature(method)
            aws_connector_mock_signature = inspect.signature(
                aws_connector_mock_methods[method_name]
            )

            # If signatures do not match, show the exact differences
            if str(aws_connector_signature) != str(
                aws_connector_mock_signature
            ):
                print(f"Method '{method_name}' signature mismatch:")
                print(f"AwsConnector: {aws_connector_signature}")
                print(f"AwsConnectorMock: {aws_connector_mock_signature}")

                # Fail the test and provide detailed information
                self.fail(
                    f"Method signature of '{method_name}' in AwsConnector"
                    f" and AwsConnectorMock do not match."
                    f"\nAwsConnector signature: {aws_connector_signature}"
                    f"\nAwsConnectorMock signature: "
                    f"{aws_connector_mock_signature}"
                )
