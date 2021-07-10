from unittest.mock import Mock

from rollbar import report_exc_info, report_message
from config import definitions
from api.helpers.pipeline.json_string_item_exporter import JsonStringItemExporter
from scrapy.statscollectors import StatsCollector


class SQSPushStep:
    """
    Will push to an SQS queue all items present in the scrapy pipeline
    """

    STATISTICS_KEY = 'sqs_push_steps/pushed_count'

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def __init__(self, stats: StatsCollector):
        self.enabled = False
        self._type = str(type(self))
        self.exporter = JsonStringItemExporter()
        self.queue = None
        self.stats = stats

    def open_spider(self, spider):
        self.stats.set_value(SQSPushStep.STATISTICS_KEY, 'N/A')
        uri = definitions.get_output_queue_url()
        if uri is None:
            spider.logger.warn('Missing SQS uri in ' + self._type)
            return

        try:
            region = definitions.get_output_queue_region()
            spider.logger.info('On spider open, just opened ' + self._type + ' for SQS ' + uri + ' in region ' + region)
            self.enabled = False
            self.queue = Mock()
            self.stats.set_value(SQSPushStep.STATISTICS_KEY, 0)
        except BaseException as e:
            spider.logger.warn(f'Could not enable SQS push in {self._type}', exc_info=True)
            report_exc_info(exc_info=e, level="critical")

    def close_spider(self, spider):
        spider.logger.info('On spider close, just closed ' + self._type)
        report_message(f'Admin_doc collect v2 ended successfuly for start_url {spider.start_url}', level='info')

    def process_item(self, item, spider):
        if self.enabled:
            content = self.exporter.export(item)
            spider.logger.debug("Will send JSON: " + str(content))

            response = self.queue.send_message(MessageBody=content)
            self.stats.inc_value(SQSPushStep.STATISTICS_KEY)
            spider.logger.debug('Just sent a message to SQS: response=' + str(response))

        return item
