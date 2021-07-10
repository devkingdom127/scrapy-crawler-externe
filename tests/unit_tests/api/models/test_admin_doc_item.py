from unittest import TestCase
from unittest.mock import sentinel

from api.models.admin_doc_item import AdminDocItem


class TestAdminDocItem(TestCase):

    def test_property_url(self):
        url = sentinel.url
        sut = AdminDocItem(url=url)

        self.assertEqual(sut['url'], url)

    def test_property_responseMimeContentType(self):
        response_mime_content_type = sentinel.responseMimeContentType
        sut = AdminDocItem(responseMimeContentType=response_mime_content_type)

        self.assertEqual(sut['responseMimeContentType'], response_mime_content_type)

    def test_property_locations(self):
        locations = sentinel.locations
        sut = AdminDocItem(locations=locations)

        self.assertEqual(sut['locations'], locations)

    def test_property_dataProvider(self):
        data_provider = sentinel.dataProvider
        sut = AdminDocItem(dataProvider=data_provider)

        self.assertEqual(sut['dataProvider'], data_provider)

    def test_property_operationId(self):
        operation_id = sentinel.operationId
        sut = AdminDocItem(operationId=operation_id)

        self.assertEqual(sut['operationId'], operation_id)

    def test_non_existing_property_raise(self):
        sut = AdminDocItem()

        with self.assertRaises(KeyError):
            should_raise = sut['field_that_not_exists']
            print(should_raise)
