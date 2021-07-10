import json

from scrapy import Item
from scrapy.exporters import BaseItemExporter
from scrapy.utils.serialize import ScrapyJSONEncoder


class JsonStringItemExporter(BaseItemExporter):
    """
    Hijacked the Item serializer to our purpose
    """

    def __init__(self, **kwargs):
        super().__init__(dont_fail=True, **kwargs)
        self._kwargs.setdefault('ensure_ascii', not self.encoding)
        self.encoder = ScrapyJSONEncoder(**self._kwargs)

    def export(self, item: Item) -> str:
        itemdict = dict(self._get_serialized_fields(item))
        return json.dumps(itemdict, ensure_ascii=False)
