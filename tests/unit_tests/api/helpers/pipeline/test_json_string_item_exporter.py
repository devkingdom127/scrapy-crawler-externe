from unittest import TestCase
from unittest.mock import Mock, patch

from api.helpers.pipeline.json_string_item_exporter import JsonStringItemExporter
from scrapy.utils.serialize import ScrapyJSONEncoder


class TestJsonStringItemExporter(TestCase):

    def setUp(self) -> None:
        self.sut = JsonStringItemExporter()

    @patch('scrapy.exporters.BaseItemExporter._get_serialized_fields')
    @patch('json.dumps')
    def test_export_returns_a_json_dump(self, dumps_mock, parent_method_mock):
        parent_method_mock.return_value = {'toto': 1}

        expected = Mock()
        dumps_mock.return_value = expected

        actual = self.sut.export(Mock())

        self.assertEqual(expected, actual)

    @patch('scrapy.exporters.BaseItemExporter._get_serialized_fields')
    @patch('json.dumps')
    def test_export_calls_json_dump(self, dumps_mock, parent_method_mock):
        input = {'toto': 1}
        parent_method_mock.return_value = input

        self.sut.export(Mock())

        dumps_mock.assert_called_once_with(input, ensure_ascii=False)

    def test_init_encoder_is_correct(self):
        self.assertIsInstance(self.sut.encoder, ScrapyJSONEncoder)
