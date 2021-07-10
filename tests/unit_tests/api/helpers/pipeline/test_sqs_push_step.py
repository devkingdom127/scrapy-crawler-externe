from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock, sentinel

from api.helpers.pipeline.sqs_push_step import SQSPushStep
from scrapy.statscollectors import StatsCollector


@patch('api.helpers.pipeline.sqs_push_step.definitions.get_output_queue_url')
@patch('api.helpers.pipeline.sqs_push_step.definitions.get_output_queue_region')
class TestSQSPushPipeline(TestCase):

    def setUp(self) -> None:
        self.mock_stat = MagicMock(StatsCollector)
        self.sqs_push_step = SQSPushStep(self.mock_stat)
        self.dummy_url = 'the_yellow_brick_road'
        self.dummy_region = 'paradise'

    def test_from_crawler(self, _get_region_mock, get_url_mock):
        mock_crawler = Mock()
        mock_crawler.stats = sentinel.stats

        actual = SQSPushStep.from_crawler(mock_crawler)

        self.assertEqual(actual.stats, mock_crawler.stats)

    def test_open_spider__when_no_uri__calls_spider_logger(self, _get_region_mock, get_url_mock):
        get_url_mock.return_value = None
        spider_mock = Mock()

        self.sqs_push_step.open_spider(spider_mock)

        spider_mock.logger.warn.assert_called_once_with(
            "Missing SQS uri in <class 'api.helpers.pipeline.sqs_push_step.SQSPushStep'>"
        )

    @patch('api.helpers.pipeline.sqs_push_step.report_exc_info')
    def test_open_spider__when_exception__calls_spider_logger(self, mock_rollbar, get_region_mock, get_url_mock):
        get_url_mock.return_value = self.dummy_url
        get_region_mock.side_effect = ValueError
        spider_mock = Mock()

        self.sqs_push_step.open_spider(spider_mock)

        mock_rollbar.assert_called()
        spider_mock.logger.warn.assert_called_once_with(
            "Could not enable SQS push in <class 'api.helpers.pipeline.sqs_push_step.SQSPushStep'>",
            exc_info=True
        )

    @patch('api.helpers.pipeline.sqs_push_step.boto3')
    def test_open_spider__when_uri__calls_spider_logger(self, _boto3_mock, get_region_mock, get_url_mock):
        get_region_mock.return_value = self.dummy_region
        get_url_mock.return_value = self.dummy_url
        spider_mock = Mock()

        self.sqs_push_step.open_spider(spider_mock)

        spider_mock.logger.info.assert_called_once_with(
            "On spider open, just opened <class 'api.helpers.pipeline.sqs_push_step.SQSPushStep'> "
            + "for SQS the_yellow_brick_road in region paradise")

    @patch('api.helpers.pipeline.sqs_push_step.boto3')
    def test_open_spider__when_uri__opens_sqs_resource(self, boto3_mock, get_region_mock, get_url_mock):
        get_region_mock.return_value = self.dummy_region
        get_url_mock.return_value = self.dummy_url
        spider_mock = Mock()

        self.sqs_push_step.open_spider(spider_mock)

        boto3_mock.resource.assert_called_once_with('sqs', region_name='paradise')

    @patch('api.helpers.pipeline.sqs_push_step.report_message')
    def test_close_spider__calls_spider_logger(self, mock_rollbar, _get_region_mock, _get_url_mock):
        spider_mock = Mock(start_url=Mock())

        self.sqs_push_step.close_spider(spider_mock)

        spider_mock.logger.info.assert_called_once_with(
            "On spider close, just closed <class 'api.helpers.pipeline.sqs_push_step.SQSPushStep'>"
        )
        mock_rollbar.assert_called_with(
            f'Admin_doc collect v2 ended successfuly for start_url {spider_mock.start_url}',
            level='info'
        )

    def test_process__when_disabled__returns_input(self, _get_region_mock, _get_url_mock):
        spider_mock = Mock()
        item_mock = Mock()

        actual = self.sqs_push_step.process_item(item_mock, spider_mock)

        self.assertEqual(actual, item_mock)

    def test_process__when_disabled__does_not_send_to_sqs(self, _get_region_mock, _get_url_mock):
        spider_mock = Mock()
        item_mock = Mock()

        queue_mock = Mock()
        self.sqs_push_step.queue = queue_mock

        self.sqs_push_step.process_item(item_mock, spider_mock)

        queue_mock.assert_not_called()

    def test_process__when_enabled__pushes_to_SQS(self, _get_region_mock, _get_url_mock):
        spider_mock = Mock()
        item_mock = Mock()

        exporter_mock = Mock()
        self.sqs_push_step.exporter = exporter_mock
        self.sqs_push_step.enabled = True

        queue_mock = Mock()
        self.sqs_push_step.queue = queue_mock

        serialized_message_mock = Mock()
        exporter_mock.export.return_value = serialized_message_mock

        self.sqs_push_step.process_item(item_mock, spider_mock)

        queue_mock.send_message.assert_called_once_with(MessageBody=serialized_message_mock)

    def test_process__when_enabled__returns_input(self, _get_region_mock, _get_url_mock):
        spider_mock = Mock()
        item_mock = Mock()

        exporter_mock = Mock()
        self.sqs_push_step.exporter = exporter_mock
        self.sqs_push_step.enabled = True

        queue_mock = Mock()
        self.sqs_push_step.queue = queue_mock

        actual = self.sqs_push_step.process_item(item_mock, spider_mock)

        self.assertEqual(actual, item_mock)

    def test_process__when_enabled__serializes_input(self, _get_region_mock, _get_url_mock):
        spider_mock = Mock()
        item_mock = Mock()

        exporter_mock = Mock()
        self.sqs_push_step.exporter = exporter_mock
        self.sqs_push_step.enabled = True

        queue_mock = Mock()
        self.sqs_push_step.queue = queue_mock

        self.sqs_push_step.process_item(item_mock, spider_mock)

        exporter_mock.export.assert_called_once_with(item_mock)

    def test_process__when_enabled__calls_stats(self, _get_region_mock, _get_url_mock):
        self.sqs_push_step.exporter = Mock()
        self.sqs_push_step.queue = Mock()
        self.sqs_push_step.enabled = True

        self.sqs_push_step.process_item(Mock(), Mock())

        self.mock_stat.inc_value.assert_called_once_with('sqs_push_steps/pushed_count')
