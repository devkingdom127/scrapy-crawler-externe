from unittest import TestCase
from unittest.mock import patch, Mock, sentinel
from freezegun.api import freeze_time

from api.services.crawler import Crawler


@patch('api.services.crawler.admin_doc_scraper')
class TestCrawler(TestCase):

    def setUp(self) -> None:
        self.operation_uid = "23072020_17h00m00s000000_testuser"
        self.user = "testuser"

    @freeze_time("2020-07-23 17:00:00")
    def test_run__dispatches_task(self, task_mock):
        start_url = Mock()
        locations = [dict(uid=str(sentinel.territory_uid))]
        parameters = dict(
            crawler_options=dict(
                start_url=start_url,
                locations=locations,
                user=self.user
            )
        )

        Crawler.run(parameters)

        task_mock.assert_called_once_with(
            start_url=start_url,
            locations=locations,
            operation_uid=self.operation_uid
        )

    @freeze_time("2020-07-23 17:00:00")
    def test_run__returns_taskid(self, _task_mock):
        parameters = dict(
            crawler_options=dict(
                start_url=Mock(),
                locations=Mock(),
                user=self.user
            )
        )

        actual = Crawler.run(parameters)

        self.assertEqual(actual, self.operation_uid)
