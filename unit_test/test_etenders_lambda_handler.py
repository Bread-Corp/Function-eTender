import unittest
import json
from unittest.mock import patch, Mock
import sys
import os

# Patch boto3 before importing lambda_handler
mock_boto3 = Mock()
mock_boto3.client.return_value = Mock()
sys.modules['boto3'] = mock_boto3

import lambda_handler

class TestETendersLambdaHandler(unittest.TestCase):

    @patch('lambda_handler.requests.get')
    @patch('lambda_handler.sqs_client.send_message_batch')
    @patch('lambda_handler.eTender.from_api_response')
    def test_lambda_handler_success(self, mock_from_api, mock_sqs, mock_get):
        with open(os.path.join('unit_test', 'test_data', 'sample_etenders.json'), 'r') as f:
            sample_data = json.load(f)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json = lambda: {"data": sample_data}
        mock_get.return_value = mock_response

        mock_tender = Mock()
        mock_tender.to_dict.return_value = {"title": "Valid eTender"}
        mock_from_api.return_value = mock_tender

        mock_sqs.return_value = {"Successful": [{"Id": "tender_message_0_0"}]}

        result = lambda_handler.lambda_handler({}, {})
        self.assertEqual(result['statusCode'], 200)
        self.assertIn("Tender data processed", result['body'])

    @patch('lambda_handler.requests.get')
    def test_lambda_handler_fetch_fail(self, mock_get):
        mock_get.side_effect = lambda_handler.requests.exceptions.RequestException("Network error")
        result = lambda_handler.lambda_handler({}, {})
        self.assertEqual(result['statusCode'], 502)
        self.assertIn("Failed to fetch data from source API", result['body'])

    @patch('lambda_handler.requests.get')
    def test_lambda_handler_invalid_json(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_get.return_value = mock_response

        result = lambda_handler.lambda_handler({}, {})
        self.assertEqual(result['statusCode'], 502)
        self.assertIn("Invalid JSON response", result['body'])

    @patch('lambda_handler.requests.get')
    @patch('lambda_handler.sqs_client.send_message_batch')
    @patch('lambda_handler.eTender.from_api_response')
    def test_lambda_handler_with_sqs_failure(self, mock_from_api, mock_sqs, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json = lambda: {"data": [{"id": "123"}]}
        mock_get.return_value = mock_response

        mock_tender = Mock()
        mock_tender.to_dict.return_value = {"title": "Valid eTender"}
        mock_from_api.return_value = mock_tender

        mock_sqs.return_value = {
            "Successful": [],
            "Failed": [{"Id": "tender_message_0_0", "Message": "AccessDenied"}]
        }

        result = lambda_handler.lambda_handler({}, {})
        self.assertEqual(result['statusCode'], 200)
        self.assertIn("Tender data processed", result['body'])

if __name__ == '__main__':
    unittest.main()
