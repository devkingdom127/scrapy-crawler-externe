import json
from unittest import TestCase
from unittest.mock import sentinel, Mock, patch, ANY

from scrapy import Request, FormRequest
from scrapy.http import HtmlResponse, TextResponse, Response
from api.helpers.spiders.admin_doc_spider import AdminDocSpider
from api.helpers.spiders.extended_link_extractor import ExtendedLinkExtractor
from api.helpers.utils.settings_loader import SettingsLoader


class Globals:
    post_endpoint_config = {
        "http://endpoint/url": {
            "url": "http://endpoint/url",
            "payload": {"param1": "a", "param2": "b", "page": "1"},
            "query_string": {"p1": "1", "p2": "2"},
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "max_page": 2,
            "page_field": "page",
        }
    }


class MockSettingLoader(SettingsLoader):
    @staticmethod
    def load_config():
        return None

    def get_allowed_cdn(self):
        """Return custom allowed CDN that can be visited because they can host data."""
        return ["an_allowed_cdn"]

    def get_allowed_domain(self):
        """Return out of site domains that can be visited because they can host data."""
        return ["an_allowed_domain"]

    def get_denied_pattern(self):
        """Return custom denied link patterns (calendar, search engine...)."""
        return ["a_denied_pattern"]

    def get_denied_domain(self):
        """Return domain not to visit (facebook, twitter, météofrance...)."""
        return ["a_denied_domain"]

    def get_post_endpoints(self):
        """Return post endpoints."""
        return Globals.post_endpoint_config


class MockLinkExtractor(ExtendedLinkExtractor):
    @staticmethod
    def is_redirected(url):
        return url, False


@patch("api.helpers.spiders.admin_doc_spider.ItemYielder")
@patch("api.helpers.spiders.admin_doc_spider.CalendarLinkFilter")
class TestAdminDocSpider(TestCase):
    class DummyResponse(TextResponse):
        pass

    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    @patch(
        "api.helpers.spiders.admin_doc_spider.ExtendedLinkExtractor", MockLinkExtractor
    )
    def setUp(self) -> None:
        self.locations = [{"name": "A location", "uid": "FRCOMMXXX"}]
        self.start_url = "http://www.perdu.com/index.html"
        self.operation_uid = sentinel.operation_uid
        self.admin_doc_spider = AdminDocSpider(
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
        )

    def test_init__sets_start_urls(self, *_args):
        self.assertEqual(self.admin_doc_spider.start_urls, [self.start_url])

    def test_init__sets_allowed_domains(self, *_args):
        self.assertSetEqual(
            self.admin_doc_spider.allowed_domains, {"www.perdu.com", "an_allowed_cdn"}
        )

    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    @patch(
        "api.helpers.spiders.admin_doc_spider.ExtendedLinkExtractor", MockLinkExtractor
    )
    def test_from_crawler__returns_spider(self, mock_calendar_filter, *_args):
        actual = AdminDocSpider.from_crawler(
            crawler=Mock(),
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
        )

        self.assertEqual(
            actual.calendar_link_filter, mock_calendar_filter.from_crawler.return_value
        )

    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    @patch(
        "api.helpers.spiders.admin_doc_spider.ExtendedLinkExtractor", MockLinkExtractor
    )
    def test_from_crawler__pass_crawler_to_calendar_filter(
            self, mock_calendar_filter, *_args
    ):
        crawler = Mock()
        AdminDocSpider.from_crawler(
            crawler=crawler,
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
        )

        mock_calendar_filter.from_crawler.assert_called_once_with(crawler)

    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    @patch(
        "api.helpers.spiders.admin_doc_spider.ExtendedLinkExtractor", MockLinkExtractor
    )
    def test_parse_response__when_not_an_htmlresponse__yields_an_item(
            self, _, mock_item_yielder
    ):
        sut = AdminDocSpider(
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
        )
        input = TestAdminDocSpider.DummyResponse(self.start_url)
        mock_item_yielder.return_value.get_content_type.return_value = (
            sentinel.content_type,
            sentinel.is_valid,
        )
        mock_item_yielder.return_value.from_response.return_value = [
            sentinel.from_item_yielder
        ]

        actual = sut.parse_response(input)
        self.assertEqual(list(actual), [sentinel.from_item_yielder])

    @patch("api.helpers.spiders.admin_doc_spider.AdminDocSpider.parse_from_endpoint")
    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    @patch(
        "api.helpers.spiders.admin_doc_spider.ExtendedLinkExtractor", MockLinkExtractor
    )
    def test_parse_response__when_post_endpoint(
            self, mck_parse_endpoint, _, mock_item_yielder
    ):
        sut = AdminDocSpider(
            start_url="http://endpoint/url",
            locations=self.locations,
            operation_uid=self.operation_uid,
        )
        input2 = TestAdminDocSpider.DummyResponse("http://endpoint/url")
        mock_item_yielder.return_value.get_content_type.return_value = (
            sentinel.content_type,
            sentinel.is_valid,
        )
        mck_parse_endpoint.return_value = [Mock(spec=FormRequest)]

        list(sut.parse_response(input2))

        mck_parse_endpoint.assert_called_with(
            Globals.post_endpoint_config["http://endpoint/url"]
        )

    @patch("api.helpers.spiders.admin_doc_spider.AdminDocSpider.parse_json")
    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    @patch(
        "api.helpers.spiders.admin_doc_spider.ExtendedLinkExtractor", MockLinkExtractor
    )
    def test_parse_response__when_json_response(
            self, mck_parse_json, _, mock_item_yielder
    ):
        sut = AdminDocSpider(
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
        )
        input2 = Response(
            url=self.start_url, headers={"content-type": "application/json"}
        )

        mock_item_yielder.return_value.get_content_type.return_value = (
            "application/json",
            sentinel.is_valid,
        )
        mck_parse_json.return_value = [Mock(spec=FormRequest)]

        list(sut.parse_response(input2))

        mck_parse_json.assert_called_with(input2)

    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    def test_parse_response__when_not_an_htmlresponse__calls_item_yielder(
            self, _, mock_item_yielder
    ):
        sut = AdminDocSpider(
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
        )
        input = TestAdminDocSpider.DummyResponse(self.start_url)
        mock_item_yielder.return_value.get_content_type.return_value = (
            sentinel.content_type,
            sentinel.is_valid,
        )

        list(sut.parse_response(input))

        mock_item_yielder.return_value.from_response.assert_called_once_with(input, sut)

    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    def test_parse_response__when_an_htmlresponse_with_ctype_valid__calls_item_yielder(
            self, _, mock_item_yielder
    ):
        sut = AdminDocSpider(
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
        )
        input = Mock(spec=HtmlResponse)
        mock_item_yielder.return_value.get_content_type.return_value = (
            sentinel.content_type,
            True,
        )

        list(sut.parse_response(input))

        mock_item_yielder.return_value.from_response.assert_called_once_with(input, sut)

    @patch("api.helpers.spiders.admin_doc_spider.ItemYielder.get_content_type")
    def test_parse_response__when_an_htmlresponse_without_link__yields_nothing(
            self, mk_get_content_type, *_args
    ):
        input = Mock(spec=HtmlResponse)
        input.xpath.return_value.getall.return_value = []

        mk_get_content_type.return_value = (sentinel.content_type, False)

        actual = self.admin_doc_spider.parse_response(input)

        self.assertEqual(list(actual), [])

    @patch("api.helpers.spiders.admin_doc_spider.ItemYielder.get_content_type")
    def test_parse_response__when_an_htmlresponse_with_invalid_link__yields_nothing(
            self, mk_get_content_type, *_args
    ):
        input = Mock(spec=HtmlResponse)
        input.xpath.return_value.getall.return_value = ["x"]
        input.urljoin.return_value.startswith.return_value = False
        input.urljoin.return_value = "anurl"
        mk_get_content_type.return_value = (sentinel.content_type, False)

        actual = self.admin_doc_spider.parse_response(input)

        self.assertEqual(list(actual), [])

    @patch("api.helpers.spiders.admin_doc_spider.ItemYielder.get_content_type")
    @patch("api.helpers.spiders.admin_doc_spider.scrapy.Request")
    @patch("api.helpers.spiders.admin_doc_spider.ExtendedLinkExtractor.matches")
    def test_parse_response__when_an_htmlresponse_with_valid_link__yields_a_request(
            self, mk_link_extractor_matches, mock_request, mk_get_content_type, *_args
    ):
        input = Mock(spec=HtmlResponse)
        input.xpath.return_value.getall.return_value = ["x"]
        mk_link_extractor_matches.return_value = True
        input.urljoin.return_value.startswith.side_effect = [True, False]
        req = sentinel.request
        mock_request.return_value = req
        mk_get_content_type.return_value = (sentinel.content_type, False)

        actual = self.admin_doc_spider.parse_response(input)

        self.assertEqual(list(actual), [req])

    @patch("api.helpers.spiders.admin_doc_spider.ItemYielder.get_content_type")
    @patch("api.helpers.spiders.admin_doc_spider.scrapy.Request")
    @patch("api.helpers.spiders.admin_doc_spider.ExtendedLinkExtractor.matches")
    def test_parse_response__when_an_htmlresponse_with_valid_link__yields_a_proper_request(
            self, mk_link_extractor_matches, mock_request, mk_get_content_type, *_args
    ):
        input = Mock(spec=HtmlResponse)
        input.xpath.return_value.getall.return_value = ["x"]
        mk_link_extractor_matches.return_value = True
        input.urljoin.return_value.startswith.side_effect = [True, False]
        mk_get_content_type.return_value = (sentinel.content_type, False)

        list(
            self.admin_doc_spider.parse_response(input)
        )  # list() forces the generator to run
        mock_request.assert_called_once_with(
            input.urljoin.return_value, callback=self.admin_doc_spider.parse_response
        )

    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    def test_parse__when_not_htmlresponse__yields_an_item(self, _, mock_item_yielder):
        sut = AdminDocSpider(
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
        )
        sut._follow_links = True
        input = TestAdminDocSpider.DummyResponse(self.start_url)
        mock_item_yielder.return_value.from_response.return_value = [
            sentinel.from_item_yielder
        ]

        actual = sut.parse(input)

        self.assertEqual(list(actual), [sentinel.from_item_yielder])

    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    def test_parse__when_not_htmlresponse__calls_item_yielder(
            self, _, mock_item_yielder
    ):
        sut = AdminDocSpider(
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
        )
        sut._follow_links = True
        input = TestAdminDocSpider.DummyResponse(self.start_url)

        list(sut.parse(input))

        mock_item_yielder.return_value.from_response.assert_called_once_with(input, sut)

    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    @patch("api.helpers.spiders.admin_doc_spider.ItemYielder.get_content_type")
    @patch("api.helpers.spiders.admin_doc_spider.ExtendedLinkExtractor.matches")
    def test_parse__when_htmlresponse__yields_request(
            self, mk_matches, mk_get_content_type, *_args
    ):
        sut = AdminDocSpider(
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
        )
        sut.calendar_link_filter = Mock(keep=Mock(return_value=True))
        sut._follow_links = True

        def f(*args):
            return sentinel.content_type, False

        sut.item_yielder.get_content_type = f
        mk_matches.return_value = True
        random_url = "http://ohcrap.ie"
        input = HtmlResponse(
            self.start_url, body=f'<a href="{random_url}">x</a>', encoding="utf-8"
        )

        actual = list(sut.parse_response(input))
        self.assertEqual(1, len(actual))
        self.assertIsInstance(actual[0], Request)
        self.assertEqual(random_url, actual[0].url)

    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    @patch("api.helpers.spiders.admin_doc_spider.Rule")
    def test_init__rule_has_errback(self, mock_rule, *_args):
        sut = AdminDocSpider(
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
        )

        mock_rule.assert_called_once_with(
            callback=sut.parse_response,
            errback=sut.errback,
            link_extractor=ANY,
            process_links=sut.process_links,
            follow=True,
        )

    def test_errback__logs(self, *_args):
        with self.assertLogs() as l_cm:
            self.admin_doc_spider.errback("crap")

        self.assertEqual(l_cm.output, ["ERROR:admindoc:'crap'"])

    @patch("api.helpers.spiders.admin_doc_spider.report_message")
    @patch("api.helpers.spiders.admin_doc_spider.AdminDocSpider.is_timeout_on_domain")
    def test_report_rollbar_when_crawler_timeout_on_domain(
            self, mock_timeout, mock_message, *_args
    ):
        absolute_href = "http://test.com/index.html"
        self.admin_doc_spider.explored_sub_domains["test.com"] = {
            "start_at": sentinel.start_at,
            "crawler_count": 5,
            "is_reported": False,
        }
        mock_timeout.return_value = True
        self.admin_doc_spider.report_timeout(absolute_href)
        mock_message.assert_called_once_with(
            "Domain test.com timeout with 6 visits", level="warning"
        )

    @patch("api.helpers.spiders.admin_doc_spider.report_message")
    def test_not_call_report_rollbar_when_crawler_non_in_timeout_on_domain(
            self, mock_message, *_args
    ):
        absolute_href = "http://www.test.com/index.html"
        self.admin_doc_spider.report_timeout(absolute_href)
        mock_message.assert_not_called()

    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    @patch(
        "api.helpers.spiders.admin_doc_spider.ExtendedLinkExtractor", MockLinkExtractor
    )
    @patch("api.helpers.spiders.admin_doc_spider.scrapy.Request")
    def test_json_parser(self, mck_req, *args):
        sut = AdminDocSpider(
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
        )
        json_body = {
            "content": "a_content",
            "documents": {
                "fichier": [
                    {
                        "metadata": {},
                        "url": "/relative/path/to/file.pdf",
                        "mime_type": "application/pdf",
                    }
                ]
            },
        }
        input = TextResponse(
            url="http://an_url/another_path",
            body=json.dumps(json_body),
            encoding="utf-8",
        )
        list(sut.parse_json(input))

        mck_req.assert_called_with(
            "http://an_url/relative/path/to/file.pdf", callback=sut.parse_response
        )

    @patch("api.helpers.spiders.admin_doc_spider.SettingsLoader", MockSettingLoader)
    @patch(
        "api.helpers.spiders.admin_doc_spider.ExtendedLinkExtractor", MockLinkExtractor
    )
    @patch("api.helpers.spiders.admin_doc_spider.FormRequest")
    def test_parse_from_endpoint(self, mck_form_req, *args):
        sut = AdminDocSpider(
            start_url=self.start_url,
            locations=self.locations,
            operation_uid=self.operation_uid,
        )

        list(sut.parse_from_endpoint(Globals.post_endpoint_config["http://endpoint/url"]))
        mck_form_req.assert_called_with(
            "http://endpoint/url/?p1=1&p2=2",
            method="POST",
            formdata=Globals.post_endpoint_config["http://endpoint/url"]["payload"],
            headers=Globals.post_endpoint_config["http://endpoint/url"]["headers"],
            callback=sut.parse_response
        )
