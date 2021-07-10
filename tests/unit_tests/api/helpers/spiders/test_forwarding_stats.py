from unittest import TestCase
from unittest.mock import Mock, MagicMock, sentinel, patch

from api.helpers.spiders.forwarding_stats import ForwardingStats


@patch('api.helpers.spiders.forwarding_stats.PensieveAccessor')
class TestForwardingStats(TestCase):

    def setUp(self) -> None:
        self.crawler = Mock()
        self.inner_stats = MagicMock()
        self.territory_uid = sentinel.territory_uid
        self.forwarding_stats = ForwardingStats(self.crawler)
        self.forwarding_stats._stats = self.inner_stats

    def test_close_spider_calls_pensieve(self, mock_pensieve):
        spider = MagicMock(collected_urls=[], locations=MagicMock())
        self.forwarding_stats.close_spider(spider, sentinel.reason)

        mock_pensieve.update_collect_operation.assert_called_once_with(
            uid=spider.operation_uid,
            status="success",
            infos={
                "stats": {},
                "territory_uid": spider.locations[0]['uid'],
                "collected_urls": spider.collected_urls
            }
        )
