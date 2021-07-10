from scrapy.exceptions import DropItem


class NoDuplicateStep:
    """
    Will discard already extracted URLs
    """

    def __init__(self):
        self._type = str(type(self))
        self.seen_urls = set()

    def open_spider(self, spider):
        spider.logger.info('On spider open, just opened ' + self._type)

    def close_spider(self, spider):
        spider.logger.info('On spider close, just closed ' + self._type)

    def process_item(self, item, spider):
        url = item['url']
        if url in self.seen_urls:
            raise DropItem("Duplicate item found: %s" % url)
        else:
            self.seen_urls.add(url)
            return item
