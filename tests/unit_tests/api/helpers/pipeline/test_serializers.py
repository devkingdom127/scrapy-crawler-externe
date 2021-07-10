from unittest import TestCase

from config.definitions import Cst
from api.helpers.pipeline.serializers import location_serializer


class TestSerializers(TestCase):
    def setUp(self) -> None:
        self.input_locations = [{'name': 'Drôme', 'uid': 'FRCOMM44234'}]
        self.expected_output = [{"FRCOMM44234": [Cst.PUBLISHER]}]

    def test_locations_are_serialized_correctly(self):
        serialized_locations = location_serializer(self.input_locations)
        self.assertListEqual(serialized_locations, self.expected_output)
