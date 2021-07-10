import datetime
import re
from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch, sentinel

from freezegun import freeze_time
from api.helpers.spiders.calendar_link_filter import CalendarLinkFilter
from scrapy.link import Link
from scrapy.statscollectors import StatsCollector


@freeze_time(datetime.date(2020, 7, 14))
class TestCalendarLinkFilter(TestCase):

    def setUp(self) -> None:
        self.mock_stat = MagicMock(StatsCollector)
        self.sut = CalendarLinkFilter(self.mock_stat)

    def test_from_crawler(self):
        mock_crawler = Mock()
        mock_crawler.stats = sentinel.stats

        actual = CalendarLinkFilter.from_crawler(mock_crawler)

        self.assertEqual(actual.stats, mock_crawler.stats)

    def test_regex_no_matching_cal_ok(self):
        mock_request = Mock(url='xxx')

        actual = self.sut.keep(mock_request)

        self.assertTrue(actual)

    def test_regex_no_matching_cal_calls_stats(self):
        mock_request = Mock(url='xxx')

        self.sut.keep(mock_request)

        self.mock_stat.inc_value.assert_called_once_with('calendar_link_filter/none/keep_count')

    def test_regex_simple_match_ok(self):
        mock_request = Mock(url='/iccaldate=')

        actual = self.sut.keep(mock_request)

        self.assertFalse(actual)

    def test_regex_simple_match_calls_stats(self):
        mock_request = Mock(url='/iccaldate=')

        self.sut.keep(mock_request)

        self.mock_stat.inc_value.assert_called_once_with('calendar_link_filter/iccaldate/skip_count')

    def test_regex_within_range_ok(self):
        mock_request = Mock(url='?truc=12&tx_cimplanning_displayplannings[y]=2020&whatever')

        actual = self.sut.keep(mock_request)

        self.assertTrue(actual)

    def test_regex_within_range_calls_stats(self):
        mock_request = Mock(url='?truc=12&tx_cimplanning_displayplannings[y]=2020&whatever')

        self.sut.keep(mock_request)

        self.mock_stat.inc_value.assert_called_once_with(
            'calendar_link_filter/tx_cimplanning_displayplannings/keep_count')

    def test_regex_below_threshold_raise(self):
        mock_request = Mock(url='?truc=12&tx_cimplanning_displayplannings[y]=1947&whatever')

        actual = self.sut.keep(mock_request)

        self.assertFalse(actual)

    def test_regex_below_threshold_calls_stats(self):
        mock_request = Mock(url='?truc=12&tx_cimplanning_displayplannings[y]=1947&whatever')

        self.sut.keep(mock_request)

        self.mock_stat.inc_value.assert_called_once_with(
            'calendar_link_filter/tx_cimplanning_displayplannings/skip_count')

    def test_regex_above_threshold_raise(self):
        mock_request = Mock(url='?truc=12&tx_cimplanning_displayplannings[y]=2080&whatever')

        actual = self.sut.keep(mock_request)

        self.assertFalse(actual)

    def test_regex_above_threshold_calls_stats(self):
        mock_request = Mock(url='?truc=12&tx_cimplanning_displayplannings[y]=2080&whatever')

        self.sut.keep(mock_request)

        self.mock_stat.inc_value.assert_called_once_with(
            'calendar_link_filter/tx_cimplanning_displayplannings/skip_count')

    @patch('api.helpers.spiders.calendar_link_filter.re', wraps=re)
    def test_loop_should_end_after_first_match_when_no_year(self, mock_re):
        special_configuration = [
            ('crap1', r"crap", ''),
            ('crap2', r"crap", ''),
            ('crap3', r"crap", ''),
            ('ok', r"ok", ''),
            ('crap4', r"crap", ''),
            ('crap5', r"crap", '')
        ]
        sut = CalendarLinkFilter(self.mock_stat, configuration=special_configuration)
        mock_request = Mock(url='ok')

        sut.keep(mock_request)

        self.assertEqual(4, len(mock_re.match.call_args_list))

    @patch('api.helpers.spiders.calendar_link_filter.re', wraps=re)
    def test_loop_should_end_after_first_match_when_year(self, mock_re):
        special_configuration = [
            ('crap1', r"hop(2020)", ''),
            ('crap2', r"hop(2020)", ''),
            ('crap3', r"crap", '')
        ]
        sut = CalendarLinkFilter(self.mock_stat, configuration=special_configuration)
        mock_request = Mock(url='hop2020')

        sut.keep(mock_request)

        self.assertEqual(1, len(mock_re.match.call_args_list))

    def test_samples__return_false(self):
        for key, _, sample in CalendarLinkFilter.CONFIG:
            with self.subTest():
                link = Link(url=sample)
                self.assertFalse(self.sut.keep(link), msg=key)
