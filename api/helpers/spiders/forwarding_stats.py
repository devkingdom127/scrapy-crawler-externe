from rollbar import report_message

from scrapy.statscollectors import MemoryStatsCollector


class ForwardingStats(MemoryStatsCollector):

    def _persist_stats(self, stats, spider):
        super()._persist_stats(stats, spider)

        to_iso_keys = ('start_time', 'finish_time')
        stats_clone = dict(stats.items())
        for key in to_iso_keys:
            if key in stats_clone:
                stats_clone[key] = stats_clone[key].isoformat()

        if not spider.collected_urls:
            message = f'No collected url for {spider.start_url}, there might be a problem'
            spider.logger.warn(message)
            report_message(message, level='warning')
