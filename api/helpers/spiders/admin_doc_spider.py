import datetime
import json
from pathlib import Path
from typing import List
from urllib.parse import urlparse, urlencode, urljoin

import scrapy
from rollbar import report_message

from api.helpers.spiders.calendar_link_filter import CalendarLinkFilter
from api.helpers.spiders.extended_link_extractor import ExtendedLinkExtractor
from api.helpers.spiders.item_yielder import ItemYielder
from scrapy import linkextractors
from scrapy.http import HtmlResponse, Response, FormRequest
from scrapy.link import Link
from scrapy.spiders import Rule, CrawlSpider

# Fix To avoid error "ValueError: invalid hostname: cdn1_2.reseaudesvilles.fr"
# CF https://stackoverflow.com/questions/41819592/scrapy-not-scrape-page-if-subdomain-have-underscore
import idna

from api.helpers.utils.settings_loader import SettingsLoader
from config import definitions
from config.definitions import Cst, visited_urls
from config.settings import PROJECT_PATH

idna.idnadata.codepoint_classes["PVALID"] = tuple(
    sorted(list(idna.idnadata.codepoint_classes["PVALID"]) + [0x5F0000005F])
)


class AdminDocSpider(CrawlSpider):
    """
    This is the main class for this library.

    The detailed documentation may be found at https://docs.scrapy.org/en/latest/topics/spiders.html#crawlspider
    """

    # ------
    # Our own properties

    #: This dictionary is thus: "extension: mime type"
    # This should be the only editing place to add a new kind of supported document

    ACCEPTED_MIME_TYPES = {"pdf": Cst.PDF_CONTENT_TYPE}
    #: Only follow links with those protocols
    ACCEPTED_PROTOCOLS = {"http:", "https:"}

    #: This collection lists CDN domains where territories store their valuable files.
    # Subdomains are automatically included.
    # See links on:
    # http://www.la-garde-adhemar.com/fr/information/93109/plan-local-urbanisme-%28plu%29
    # http://www.4cvs.fr/fr/information/7825/comptes-rendus
    # http://saintrestitut-mairie.fr/

    #: Those are more file extensions that we do not care about
    __MORE_IGNORED_EXT = [
        "aif",
        "arj",
        "bin",
        "cda",
        "csv",
        "dat",
        "db",
        "dbf",
        "webp",
        "deb",
        "gz",
        "key",
        "log",
        "mdb",
        "mid",
        "mpa",
        "pkg",
        "psd",
        "rpm",
        "sav",
        "sql",
        "toast",
        "vcd",
        "wpl",
        "z",
        "mp4",
    ]
    IGNORED_EXT = list(
        set(linkextractors.IGNORED_EXTENSIONS + __MORE_IGNORED_EXT)
        - ACCEPTED_MIME_TYPES.keys()
    )

    explored_sub_domains = {}
    # ------
    # Scrapy-known properties
    name = "admindoc"
    custom_settings = {
        "USER_AGENT": "Mozilla/5, .0 (Windows NT 10, .0; Win64; x64; rv:61, .0) Gecko/20100101 Firefox/61, .0",
        "DOWNLOAD_MAXSIZE": definitions.DOWNLOAD_MAXSIZE,
        "DOWNLOAD_TIMEOUT": definitions.get_download_timeout(),
        "DEPTH_LIMIT": definitions.get_depth_limit(),
        "RETRY_TIMES": definitions.get_retry_times(),
        "CLOSESPIDER_TIMEOUT": definitions.get_close_spider_timeout(),
        "DOWNLOAD_DELAY": definitions.get_download_delay(),
        "CONCURRENT_REQUESTS": definitions.get_concurrent_requests(),
    }

    # ------

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        spider.calendar_link_filter = CalendarLinkFilter.from_crawler(crawler)

        return spider

    def __init__(self, start_url: str, locations: list, operation_uid: str, **kwargs):
        # This should be done before the call to the parent constructor.
        custom_config = SettingsLoader()
        self.logger.info("Instantiating special parser for loc " + locations[0]["name"])

        self.link_extractor = ExtendedLinkExtractor(
            deny_extensions=self.IGNORED_EXT, custom_config=custom_config
        )
        self.output_path = PROJECT_PATH / "output" / visited_urls
        self.output_path.unlink(missing_ok=True)
        self.ACCEPTED_CONTENT_CDN = () + tuple(custom_config.get_allowed_cdn())
        self.rules = (
            Rule(
                callback=self.parse_response,
                errback=self.errback,
                link_extractor=self.link_extractor,
                process_links=self.process_links,
                follow=True,
            ),
        )
        super().__init__(**kwargs)
        self.logger.info("Instantiated spider with start_url=" + start_url)
        self.calendar_link_filter = None  # Will be set through from_crawler() call
        self.item_yielder = ItemYielder(
            start_url, locations, operation_uid, self.ACCEPTED_MIME_TYPES
        )

        # Kept for logging
        self.collected_urls = []
        self.locations = locations
        self.start_url = start_url
        self.operation_uid = operation_uid

        # Scrapy-known properties
        start_url, is_redirected = ExtendedLinkExtractor.is_redirected(start_url)
        if is_redirected:
            self.logger.info(
                "There is an initial redirection to a new start url=" + start_url
            )
        self.start_urls = [start_url]
        self.allowed_domains = self._prepare_cdn(start_url)

    def add_to_collected_url(self, url):
        self.collected_urls.append(url)

    def _prepare_cdn(self, start_url):
        domains = set(self.ACCEPTED_CONTENT_CDN)
        domains.add(urlparse(start_url).netloc)
        return domains

    def save_link(self, url):
        with self.output_path.open('a') as f:
            f.write(url+'\n')

    def process_links(self, links: List[Link]) -> List[Link]:
        return [link for link in links if self.calendar_link_filter.keep(link)]

    def parse_from_endpoint(self, endpoint_config):
        """
        Retrieve data from a post endpoint which config is past via endpoint config.
        :param endpoint_config:
            Exemple: {
                "url/where/to/call/endpoint":{
                    "url": "url/endpoint",
                    "payload" : {"endpoint_params": "a"}
                    "query_string": {"param1": "b"}
                    "headers"
                }
            }
        :return:
        """
        query_string = endpoint_config.get("query_string", {})
        url = endpoint_config["url"] + "/?" + urlencode(query_string)
        payload = endpoint_config.get("payload", {})
        headers = endpoint_config.get(
            "headers", {"Content-Type": "application/x-www-form-urlencoded"}
        )
        max_page = endpoint_config.get("max_page", 1)
        for page_num in range(1, max_page + 1):
            try:
                payload[endpoint_config["page_field"]] = str(page_num)
            except KeyError:
                # No pagination
                pass
            yield FormRequest(
                url,
                method="POST",
                formdata=payload,
                headers=headers,
                callback=self.parse_response,
            )

    def parse_json(self, response):
        """
        Handle json response from POST endpoints, in the form of
        {
            "content": ...
            "documents": {
                "fichier": [
                    {
                        "metadata": {...}
                        "url": /relative/path/to/file.pdf
                    }
                ]
            }
        }
        """
        content = json.loads(response.body)
        parsed_uri = urlparse(response.url)
        base_url = "{0.scheme}://{0.netloc}/".format(parsed_uri)
        try:
            for file in content["documents"]["fichier"]:
                if (
                    file["mime_type"] == Cst.PDF_CONTENT_TYPE
                    or file["mime_type"] == Cst.PDF_CONTENT_TYPE
                ):
                    yield scrapy.Request(
                        urljoin(base_url, file["url"]), callback=self.parse_response
                    )
        except KeyError:
            raise KeyError(
                f"Unable to extract content from file: content keys are {content.keys()}"
            )

    def parse_response(self, response: Response):
        (
            content_type_header,
            is_accepted_content_type,
        ) = self.item_yielder.get_content_type(response)
        self.save_link(response.url)
        if response.url in self.link_extractor.post_endpoints:
            yield from self.parse_from_endpoint(
                self.link_extractor.post_endpoints[response.url]
            )
        elif content_type_header == Cst.JSON_CONTENT_TYPE:
            yield from self.parse_json(response)
        elif isinstance(response, HtmlResponse) and not is_accepted_content_type:
            for href in response.xpath("//a/@href | //a/@data-downloadurl").getall():
                absolute_href = response.urljoin(href)
                for protocol in self.ACCEPTED_PROTOCOLS:
                    if absolute_href.startswith(
                        protocol
                    ) and self.link_extractor.matches(absolute_href):
                        yield scrapy.Request(
                            absolute_href, callback=self.parse_response
                        )
        else:
            yield from self.item_yielder.from_response(response, self)

    def errback(self, failure):
        """log all failures"""

        self.logger.error(repr(failure))

    def report_timeout(self, absolute_href):
        """
        Send a message warning to rollbar when the subdomain:
         - is not the official url
         - is not in the list of deny domain
         - has timeout process
        :param absolute_href: url crawler
        """
        sub_domain = urlparse(absolute_href).netloc
        if sub_domain not in self.start_url:
            try:
                self.explored_sub_domains[sub_domain]["crawler_count"] += 1
            except KeyError:
                self.explored_sub_domains[sub_domain] = {
                    "start_at": datetime.datetime.now(),
                    "crawler_count": 0,
                    "is_reported": False,
                }
            if (
                self.is_timeout_on_domain(sub_domain)
                and not self.explored_sub_domains[sub_domain]["is_reported"]
            ):
                self.explored_sub_domains[sub_domain]["is_reported"] = True
                report_message(
                    f'Domain {sub_domain} timeout with {self.explored_sub_domains[sub_domain]["crawler_count"]} visits',
                    level="warning",
                )

    def is_timeout_on_domain(self, sub_domain) -> bool:
        """
        Check if the duration of crawler process on a domain is more than the maximum duration allowed
        :param sub_domain: the subdomain
        :return: boolean
        """
        return self.explored_sub_domains[sub_domain][
            "start_at"
        ] < datetime.datetime.now() - datetime.timedelta(
            seconds=int(definitions.get_max_duration_crawler_alert())
        )

    def _requests_to_follow(self, response):
        """Overriding the parent class' method, because it would skip non-HTML responses"""

        self.report_timeout(response.url)
        if isinstance(response, HtmlResponse):
            # And now let the parent method do its job
            yield from super()._requests_to_follow(response)
        else:
            yield from self.item_yielder.from_response(response, self)
