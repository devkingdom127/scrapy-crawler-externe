from unittest import TestCase
from unittest.mock import patch, Mock

from config import definitions


@patch('os.getenv')
class TestConfigFunctions(TestCase):

    def test_get_pensieve_url_returns_from_getenv(self, getenv_mock):
        expected = Mock()
        getenv_mock.return_value = expected

        actual = definitions.get_pensieve_url()

        self.assertEqual(actual, expected)

    def test_get_pensieve_url_uses_correct_getenv_args(self, getenv_mock):
        getenv_mock.return_value = Mock()

        definitions.get_pensieve_url()

        getenv_mock.assert_called_once_with('ADMINDOC_CRAWLER_PENSIEVE_URL', 'http://127.0.0.1:8000')

    def test_get_output_queue_region_returns_from_getenv(self, getenv_mock):
        expected = Mock()
        getenv_mock.return_value = expected

        actual = definitions.get_output_queue_region()

        self.assertEqual(actual, expected)

    def test_get_output_queue_region_uses_correct_getenv_args(self, getenv_mock):
        getenv_mock.return_value = Mock()

        definitions.get_output_queue_region()

        getenv_mock.assert_called_once_with('ADMINDOC_CRAWLER_OUTPUT_QUEUE_REGION', 'eu-west-3')

    def test_get_output_queue_url_returns_from_getenv(self, getenv_mock):
        expected = Mock()
        getenv_mock.return_value = expected

        actual = definitions.get_output_queue_url()

        self.assertEqual(actual, expected)

    def test_get_output_queue_url_uses_correct_getenv_args(self, getenv_mock):
        getenv_mock.return_value = Mock()

        definitions.get_output_queue_url()

        getenv_mock.assert_called_once_with('ADMINDOC_CRAWLER_OUTPUT_QUEUE_URL', None)

    def test_get_error_queue_url_returns_from_getenv(self, getenv_mock):
        expected = Mock()
        getenv_mock.return_value = expected

        actual = definitions.get_error_queue_url()

        self.assertEqual(actual, expected)

    def test_get_error_queue_url_uses_correct_getenv_args(self, getenv_mock):
        getenv_mock.return_value = Mock()

        definitions.get_error_queue_url()

        getenv_mock.assert_called_once_with('ADMINDOC_CRAWLER_ERROR_QUEUE_URL', None)

    def test_get_env_returns_from_getenv(self, getenv_mock):
        expected = Mock()
        getenv_mock.return_value = expected

        actual = definitions.get_env()

        self.assertEqual(actual, expected)

    def test_get_env_uses_correct_getenv_args(self, getenv_mock):
        getenv_mock.return_value = Mock()

        definitions.get_env()

        getenv_mock.assert_called_once_with('ADMINDOC_CRAWLER_ENV', 'development')

    def test_max_duration_crawler_alert_returns_from_getenv(self, getenv_mock):
        expected = Mock()
        getenv_mock.return_value = expected

        actual = definitions.get_max_duration_crawler_alert()

        self.assertEqual(actual, expected)

    def test_max_duration_crawler_alert_uses_correct_getenv_args(self, getenv_mock):
        getenv_mock.return_value = Mock()

        definitions.get_max_duration_crawler_alert()

        getenv_mock.assert_called_once_with('DURATION_CRAWLER_ALERT', 3600)

    def test_get_download_timeout_returns_from_getenv(self, getenv_mock):
        expected = Mock()
        getenv_mock.return_value = expected

        actual = definitions.get_download_timeout()

        self.assertEqual(actual, expected)

    def test_get_download_timeout_uses_correct_getenv_args(self, getenv_mock):
        getenv_mock.return_value = Mock()

        definitions.get_download_timeout()

        getenv_mock.assert_called_once_with('ADMINDOC_CRAWLER_DOWNLOAD_TIMEOUT', 180)

    def test_get_close_spider_timeout_returns_from_getenv(self, getenv_mock):
        expected = Mock()
        getenv_mock.return_value = expected

        actual = definitions.get_close_spider_timeout()

        self.assertEqual(actual, expected)

    def test_get_close_spider_timeout_uses_correct_getenv_args(self, getenv_mock):
        getenv_mock.return_value = Mock()

        definitions.get_close_spider_timeout()

        getenv_mock.assert_called_once_with('ADMINDOC_CRAWLER_CLOSESPIDER_TIMEOUT', 0)

    def test_get_retry_times_returns_from_getenv(self, getenv_mock):
        expected = Mock()
        getenv_mock.return_value = expected

        actual = definitions.get_retry_times()

        self.assertEqual(actual, expected)

    def test_get_retry_times_uses_correct_getenv_args(self, getenv_mock):
        getenv_mock.return_value = Mock()

        definitions.get_retry_times()

        getenv_mock.assert_called_once_with('ADMINDOC_CRAWLER_RETRY_TIMES', 2)

    def test_get_depth_limit_returns_from_getenv(self, getenv_mock):
        expected = Mock()
        getenv_mock.return_value = expected

        actual = definitions.get_depth_limit()

        self.assertEqual(actual, expected)

    def test_get_depth_limit_uses_correct_getenv_args(self, getenv_mock):
        getenv_mock.return_value = Mock()

        definitions.get_depth_limit()

        getenv_mock.assert_called_once_with('ADMINDOC_CRAWLER_DEPTH_LIMIT', 0)

    def test_get_s3_config_path_returns_from_getenv(self, getenv_mock):
        expected = Mock()
        getenv_mock.return_value = expected

        actual = definitions.get_s3_config_path()

        self.assertEqual(actual, expected)

    def test_get_s3_config_path_uses_correct_getenv_args(self, getenv_mock):
        getenv_mock.return_value = Mock()

        definitions.get_s3_config_path()

        getenv_mock.assert_called_once_with('ADMINDOC_CRAWLER_S3_CONFIG', 's3-admindoc-config')

    def test_get_download_delay_returns_from_getenv(self, getenv_mock):
        expected = Mock()
        getenv_mock.return_value = expected

        actual = definitions.get_download_delay()

        self.assertEqual(actual, expected)

    def test_get_download_delay_uses_correct_getenv_args(self, getenv_mock):
        getenv_mock.return_value = Mock()

        definitions.get_download_delay()

        getenv_mock.assert_called_once_with('ADMINDOC_CRAWLER_DOWNLOAD_DELAY', 0)

    def test_get_concurrent_requests_returns_from_getenv(self, getenv_mock):
        expected = Mock()
        getenv_mock.return_value = expected

        actual = definitions.get_concurrent_requests()

        self.assertEqual(actual, expected)

    def test_get_concurrent_requests_uses_correct_getenv_args(self, getenv_mock):
        getenv_mock.return_value = Mock()

        definitions.get_concurrent_requests()

        getenv_mock.assert_called_once_with('ADMINDOC_CRAWLER_CONCURRENT_REQUESTS', 16)
