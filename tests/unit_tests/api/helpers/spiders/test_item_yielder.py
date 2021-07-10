from unittest import TestCase
from unittest.mock import sentinel, Mock

from api.models.admin_doc_item import AdminDocItem
from api.helpers.spiders.item_yielder import ItemYielder
from scrapy.http import Response


class TestItemYielder(TestCase):
    class DummyResponse(Response):
        pass

    def setUp(self) -> None:
        self.locations = sentinel.locations
        self.start_url = 'http://www.perdu.com/'
        self.operation_uid = sentinel.operation_uid
        self.accepted_mime_types = {'pdf': 'application/pdf'}
        self.spider = Mock()
        self.item_yielder = ItemYielder(
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
            accepted_mime_types=self.accepted_mime_types
        )

    def test_init__sets_locations(self, *_args):
        self.assertEqual(self.item_yielder.locations, self.locations)

    def test_init__sets_data_provider(self, *_args):
        self.assertEqual(self.item_yielder.dataProvider, self.start_url)

    def test__from_response__when_ctype_is_valid__yields_an_item(self):
        input = TestItemYielder.DummyResponse(self.start_url)
        input.headers['content-type'] = b'application/pdf'

        actual = self.item_yielder.from_response(input, self.spider)

        expected = AdminDocItem(
            dataProvider=self.start_url,
            locations=self.locations,
            responseMimeContentType='application/pdf',
            url=self.start_url,
            operationId=self.operation_uid
        )
        self.assertEqual(list(actual), [expected])

    def test__from_response__when_ctype_octet_stream_but_with_extension_valid_in_cdisposition__yields_an_item(self):
        input = TestItemYielder.DummyResponse(self.start_url)
        input.headers['content-type'] = b'application/octet-stream'
        input.headers['content-disposition'] = b'document.pdf'

        actual = self.item_yielder.from_response(input, self.spider)

        expected = AdminDocItem(
            dataProvider=self.start_url,
            locations=self.locations,
            responseMimeContentType='application/octet-stream',
            url=self.start_url,
            operationId=self.operation_uid
        )
        self.assertEqual(list(actual), [expected])

    def test__from_response__when_ctype_octet_stream_but_with_extension_valid_in_url__yields_an_item(self):
        input = TestItemYielder.DummyResponse(self.start_url+'document.pdf')
        input.headers['content-type'] = b'application/octet-stream'

        actual = self.item_yielder.from_response(input, self.spider)

        expected = AdminDocItem(
            dataProvider=self.start_url,
            locations=self.locations,
            responseMimeContentType='application/octet-stream',
            url=self.start_url+'document.pdf',
            operationId=self.operation_uid
        )
        self.assertEqual(list(actual), [expected])

    def test__from_response__when_ctype_default_and_extension_invalid__yields_nothing(self, *_args):
        input = TestItemYielder.DummyResponse(self.start_url)
        input.headers['content-type'] = b'application/octet-stream'

        actual = self.item_yielder.from_response(input, self.spider)

        self.assertEqual(list(actual), [])

    def test__from_response__when_ctype_is_invalid__yields_nothing(self, *_args):
        input = TestItemYielder.DummyResponse(self.start_url)
        input.headers['content-type'] = b'fake fake fake'

        actual = self.item_yielder.from_response(input, self.spider)

        self.assertEqual(list(actual), [])
