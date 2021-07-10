from unittest import TestCase
from unittest.mock import sentinel, Mock, patch

from scrapy.spidermiddlewares.httperror import HttpError

from scrapy.http import Response

from api.helpers.spiders.sqs_push_http_error import SQSPushHttpError
from api.models.input_message import InputMessage


class TestSQSPushHttpError(TestCase):

    def setUp(self) -> None:
        InputMessage.body = {"crawler_options": {"start_url": sentinel.url}}
        self.response = Response(url="error.url", status=403)
        self.exception = HttpError(response=self.response)

    @patch('api.helpers.spiders.sqs_push_http_error.definitions.get_error_queue_url', lambda: "error_queue_url")
    @patch('api.helpers.spiders.sqs_push_http_error.HttpErrorMiddleware.process_spider_exception')
    @patch('api.helpers.spiders.sqs_push_http_error.HttpErrorMiddleware.__init__')
    @patch('api.helpers.spiders.sqs_push_http_error.sqs_client')
    def test_send_message_error_to_sqs_dlq_when_http_error(self, mock_client, mock_parent, *_args):
        mock_parent.return_value = None
        sqs_push_http_error = SQSPushHttpError(Mock)
        sqs_push_http_error.process_spider_exception(response=self.response, exception=self.exception, spider=Mock)

        mock_client.send_message.assert_called_once_with(
            MessageBody='{"crawler_options": {"start_url": "error.url"}, "retry": 1}',
            MessageAttributes={'Error': {'DataType': 'String', 'StringValue': 'HttpError() with status 403'}},
            QueueUrl="error_queue_url"
        )

    @patch('api.helpers.spiders.sqs_push_http_error.HttpErrorMiddleware.__init__')
    @patch('api.helpers.spiders.sqs_push_http_error.boto3.client')
    def test_not_send_message_error_when_crawler_successfully_on_url(self, mock_client, mock_parent, *_args):
        mock_parent.return_value = None
        sqs_push_http_error = SQSPushHttpError(Mock)

        sqs_push_http_error.process_spider_exception(response=self.response, exception=None, spider=Mock)

        mock_client("sqs").send_message.assert_not_called()
