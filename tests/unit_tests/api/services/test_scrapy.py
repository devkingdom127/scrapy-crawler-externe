from unittest import TestCase
from unittest.mock import patch, sentinel

from api.helpers.spiders.admin_doc_spider import AdminDocSpider
from api.services.scrapy import admin_doc_scraper, custom_settings


@patch('api.services.scrapy.Event')
@patch('api.services.scrapy.init_rollbar')
@patch('api.services.scrapy.PensieveAccessor')
@patch('api.services.scrapy.CrawlerRunner')
class TestAdminDocScraper(TestCase):

    def setUp(self) -> None:
        self.locations = [{"name": "A com", "uid": "FRCODE"}]
        self.start_url = sentinel.start_url
        self.operation_uid = sentinel.operation_uid

    def test_runner_ctor_has_correct_args(self, mock_runner, _, __, ___):
        admin_doc_scraper(self.start_url, self.locations, self.operation_uid)

        mock_runner.assert_called_once_with(settings=custom_settings)

    def test_crawler_has_correct_args(self, mock_runner, _, __, ___):
        admin_doc_scraper(self.start_url, self.locations, self.operation_uid)

        mock_runner.return_value.crawl.assert_called_once_with(
            AdminDocSpider,
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid
        )
