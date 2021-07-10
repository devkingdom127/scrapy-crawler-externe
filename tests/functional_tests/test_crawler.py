from http import HTTPStatus
from unittest import TestCase
from unittest.mock import patch

from flask import Flask
from freezegun import freeze_time

from api.controllers.run import post

test_app = Flask(__name__)


@freeze_time("2000-01-01 10:20:30")
@patch('api.services.scrapy.init_rollbar')
@patch('api.services.scrapy.CrawlerRunner')
@patch('api.services.scrapy.PensieveAccessor')
class TestCrawler(TestCase):
    @patch('api.controllers.run.Crawler')
    def test_successfully_crawler(self, mk_crawler, _, __, ___):
        mock_request_json = {
           "crawler_expected_content_type": "administrative_document",
           "crawler_options": {
              "locations": [
                 {
                    "name": "Le Beausset",
                    "uid": "FRCOMM83016"
                 }
              ],
              "start_url": "http://www.saintnazaireledesert.fr",
              "user": "cron"
           },
           "crawler_type": "spider",
           "input": {}
        }
        mk_crawler.run.return_value = "01012000_10h20m30s000000_cron"

        with test_app.test_request_context("/"):
            actual = post(mock_request_json)
            self.assertEqual(actual[0], {"task-id": "01012000_10h20m30s000000_cron"})
            self.assertEqual(actual[1], 200)

    def test_return_500_when_non_conform_body(self, _, __, ___):
        with test_app.test_request_context("/"):
            actual = post({})
            print(actual)
            self.assertEqual(actual[1], HTTPStatus.INTERNAL_SERVER_ERROR)
