from unittest import TestCase
from unittest.mock import Mock

from api.helpers.pipeline.no_duplicate_step import NoDuplicateStep
from scrapy.exceptions import DropItem


class TestDuplicatesPipeline(TestCase):

    def setUp(self) -> None:
        self.sut = NoDuplicateStep()

    def test_process_item__one_url_returns_same_item(self):
        spider_mock = Mock()

        input = {'url': 'a_random_url'}
        actual = self.sut.process_item(input, spider_mock)

        self.assertEqual(actual, input)

    def test_process_item__one_url_dont_use_spider(self):
        spider_mock = Mock()

        input = {'url': 'a_random_url'}
        self.sut.process_item(input, spider_mock)

        spider_mock.assert_not_called()

    def test_process_item__two_different_url_returns_same_items(self):
        spider_mock = Mock()

        input1 = {'url': 'a_random_url'}
        input2 = {'url': 'another_url'}
        self.sut.process_item(input1, spider_mock)
        actual = self.sut.process_item(input2, spider_mock)

        self.assertEqual(actual, input2)

    def test_process_item__two_same_url_throws(self):
        spider_mock = Mock()

        input = {'url': 'a_random_url'}
        self.sut.process_item(input, spider_mock)

        with self.assertRaises(DropItem):
            self.sut.process_item(input, spider_mock)

    def test_open_spider__calls_spider_logger(self):
        spider_mock = Mock()

        self.sut.open_spider(spider_mock)

        spider_mock.logger.info.assert_called_once_with(
            "On spider open, just opened <class 'api.helpers.pipeline.no_duplicate_step.NoDuplicateStep'>")

    def test_close_spider__calls_spider_logger(self):
        spider_mock = Mock()

        self.sut.close_spider(spider_mock)

        spider_mock.logger.info.assert_called_once_with(
            "On spider close, just closed <class 'api.helpers.pipeline.no_duplicate_step.NoDuplicateStep'>")
