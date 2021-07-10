import logging
from threading import Event

from api.helpers.utils.rollbar import init_rollbar
from crochet import setup

from api.helpers.spiders.admin_doc_spider import AdminDocSpider
from api.helpers.spiders.custom import custom_spiders
from scrapy.crawler import CrawlerRunner

from config.definitions import SLEEP_DELAY

setup()
custom_settings = {
    # A dict containing the item pipelines to use, and their orders. Lower orders process before higher orders.
    "ITEM_PIPELINES": {
        "api.helpers.pipeline.no_duplicate_step.NoDuplicateStep": 200,
        "api.helpers.pipeline.sqs_push_step.SQSPushStep": 1_000,
    },
    "STATS_CLASS": "api.helpers.spiders.forwarding_stats.ForwardingStats",
    "SPIDER_MIDDLEWARES": {
        "api.helpers.spiders.sqs_push_http_error.SQSPushHttpError": 1_000
    },
}


def admin_doc_scraper(start_url, locations, operation_uid):
    """
    This is the entry point for the crawler job
    """
    logger = logging.getLogger(__name__)
    init_rollbar(start_url)

    logger.info("INIT admin_doc_scraper")
    exit_event = Event()
    runner = CrawlerRunner(settings=custom_settings)
    logger.info("INIT runner")
    uid = locations[0]["uid"]
    spider = custom_spiders.get(uid, AdminDocSpider)
    d = runner.crawl(
        spider, start_url=start_url, locations=locations, operation_uid=operation_uid
    )
    d.addBoth(lambda _: exit_event.set())
    while not exit_event.is_set():
        exit_event.wait(SLEEP_DELAY)
