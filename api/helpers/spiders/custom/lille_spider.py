from datetime import timedelta
from urllib.parse import urlencode

import requests

from api.helpers.spiders.admin_doc_spider import AdminDocSpider

import re
import datetime

from api.models.admin_doc_item import AdminDocItem
from config.definitions import Cst


class LilleSpider(AdminDocSpider):
    """
    Class to parse Lille Website. In particular, this class is designed to retrieve documents
    from the search engine.
    """

    SPECIAL_URLS = [
        "https://www.lille.fr/Votre-Mairie/Le-conseil-municipal/Comptes-rendus-des-seances-du-conseil-municipal"
    ]
    config = {
        "url": "https://deliberations.mairie-lille.fr/servlet/WebDelibSearchServlet",
        "query_string": {
            "hideRecDetail": "false",
            "recGlobale": "",
            "dtdebut": "01/01/2016",
            "dtfin": datetime.datetime.today().strftime("%d/%m/%Y"),
            "nbresults": "200",
        },
        "nb_days_intervals": 30,
        "lower_date": datetime.date(2016, 1, 1),
        "payload": {
            "Host": "deliberations.mairie-lille.fr",
            "Connection": "keep-alive",
            "Content-Length": "103",
            "Cache-Control": "max-age=0",
            "sec-ch-ua": ' Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            "sec-ch-ua-mobile": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "https://deliberations.mairie-lille.fr",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/"
                      "avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "frame",
            "Referer": "https://deliberations.mairie-lille.fr/servlet/WebDelibFieldSearchServlet",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
    }
    jslink_matcher = re.compile(
        r"javascript:f_openDoc\(\s*(?P<quote>['\"])(.*?)(?P=quote)"
    )

    def parse_search_engine_response(self, response):
        links = self.jslink_matcher.findall(str(response.content))
        for match in links:
            url = f"https://deliberations.mairie-lille.fr/files/unzip//{match[1]}"
            self.logger.debug('Found an accepted document: %s', response.url)
            yield self.yield_special_items(url)

    def yield_special_items(self, url):
        self.logger.debug("Found an accepted document: %s", url)
        self.add_to_collected_url(url)
        return AdminDocItem(
            url=url,
            responseMimeContentType=Cst.PDF_CONTENT_TYPE,
            locations=self.locations,
            dataProvider=self.start_url,
            operationId=self.operation_uid,
        )

    @staticmethod
    def construct_endpoint_url(base_url, qs, ld: datetime, ud: datetime):
        qs["dtdebut"] = ld.strftime("%d/%m/%Y")
        qs["dtfin"] = ud.strftime("%d/%m/%Y")
        url = base_url + "?" + urlencode(qs)
        return url

    def parse_response(self, response):
        if response.url in self.SPECIAL_URLS:
            yield from self.parse_special_url(response)
        super().parse_response(response)

    def parse_special_url(self, response):
        """Parse response from Lille search engine."""
        base_url = self.config["url"]
        lower_date = self.config["lower_date"]
        uper_date = lower_date + timedelta(30)
        query_string = self.config["query_string"]
        payload = self.config["payload"]
        headers = self.config["headers"]
        while lower_date < datetime.date.today():
            url = self.construct_endpoint_url(
                base_url, qs=query_string, ld=lower_date, ud=uper_date
            )
            lower_date = uper_date
            uper_date = uper_date + timedelta(30)
            search_engine_response = requests.post(url=url, data=payload, headers=headers)
            yield from self.parse_search_engine_response(search_engine_response)
