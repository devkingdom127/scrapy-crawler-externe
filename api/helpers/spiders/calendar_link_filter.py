import logging
import re
from datetime import date
from typing import List, Tuple

from scrapy.link import Link
from scrapy.statscollectors import StatsCollector


class CalendarLinkFilter():
    """
    Using regex, this will try to avoid spidering along calendars
    """

    logger = logging.getLogger(__name__)

    """
    How to detect links to skip, related to calendar?
    tuple[0]: label that represents the way the calendar is visible in the URL
    tuple[1]: a +re+-compilable string. If it has a capturing expression, it must be around the year
    tuple[2]: one URL where the regex would match

    TODO: il y a d'autre liens qui représentent des calendriers
    TODO: ajuster l'ordre de ces cas pour filtrer au plus tôt en fonction du nombre de correspondances trouvées
    """
    CONFIG: List[Tuple[str, str, str]] = [
        ('agenda', r'.*/[aA]genda/.*',
         'https://www.gourge.fr/agenda/action~oneday/exact_date~10-5-2019/'),

        ('iccaldate', r".*iccaldate=.*",
         'http://ville-auverssuroise.fr/?page=5&iccaldate=2020-03-1'),

        ('tx_cimplanning_displayplannings', r".*tx_cimplanning_displayplannings\[y\]=(\d{4}).*",
         'https://www.malakoff.fr/121/grandir/a-l-ecole/menus-de-la-restauration-scolaire.htm?tx_cimplanning_displayplannings[m]=3&tx_cimplanning_displayplannings[y]=2040'), # noqa E501

        ('date-param', r'.*[&\?]date=(\d{4})-\d{2}-\d{2}.*',
         'https://www.ville-saintpaultroischateaux.fr/-Agenda-144-.html?lang=fr&pile=oui&date=2037-09-01'),

        ('like-folders-in-path', r'.*/\d{1,2}/\d{1,2}/(\d{4})',
         'http://www.la-garde-adhemar.com/fr/salle-municipale/2179/salle-petit-rieu/1/10/2032')
    ]

    YEARS_IN_THE_FUTURE = 1
    YEARS_IN_THE_PAST = 10

    # This is how the operations of this class will be logged in the statistics module
    STAT_PREFIX = 'calendar_link_filter/'

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def __init__(self, stats: StatsCollector, configuration=CONFIG):
        self.logger.debug('Started an instance')
        self.stats = stats
        self.matchers = {k: re.compile(v) for (k, v, _) in configuration}

        current_year = date.today().year
        self.min_year_threshold = current_year - self.YEARS_IN_THE_PAST
        self.max_year_threshold = current_year + self.YEARS_IN_THE_FUTURE

    def keep(self, link: Link) -> bool:
        """

        :param link:
        :return: True the input if the crawler should keep it, False otherwise
        """

        for key, matcher in self.matchers.items():
            link_match = re.match(matcher, link.url)
            if link_match:
                try:
                    year = int(link_match.group(1))
                    if year < self.min_year_threshold or year > self.max_year_threshold:
                        self.logger.debug('Calendar SKIP for URL=%s', link.url)
                        self.stats.inc_value(CalendarLinkFilter.STAT_PREFIX + key + '/skip_count')
                        return False
                    else:
                        self.logger.debug('Calendar KEEP for URL=%s', link.url)
                        self.stats.inc_value(CalendarLinkFilter.STAT_PREFIX + key + '/keep_count')
                        return True
                except IndexError:
                    self.logger.debug('Calendar SKIP for URL=%s', link.url)
                    self.stats.inc_value(CalendarLinkFilter.STAT_PREFIX + key + '/skip_count')
                    return False

        self.stats.inc_value(CalendarLinkFilter.STAT_PREFIX + 'none/keep_count')
        return True
