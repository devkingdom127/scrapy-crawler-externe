import datetime

import requests

from api.helpers.spiders.admin_doc_spider import AdminDocSpider

import re
from urllib.parse import urlencode

from api.models.admin_doc_item import AdminDocItem
from config.definitions import Cst


class AmiensParser(AdminDocSpider):
    """
    Class to parse Amiens Website. In particular, this class is designed to retrieve documents
    from the search engine.
    """

    SPECIAL_URLS = ["https://www.amiens.fr/Institutions/Deliberations-Decisions"]
    config = {
        "url": "https://webdelib.amiens.fr/actes/php/rechercher.php",
        "docs_base_url": (
            "https://webdelib.amiens.fr/actes/php/"
            "consulter_fichier.php?POS_NUM_DOC={num_doc}"
            "&POS_NUM_PAGE={num_page}&POS_NUM_SSPAGE={spage}"
        ),
        "query_string": {
            "POS_TYPEDOC": "DDL",
            "POS_VAL_RUB_COL": "",
            "POS_VAL_CTRL_COL": "",
            "POS_VAL_RUB_TYP": "",
            "POS_VAL_CTRL_TYP": "",
            "POS_VAL_RUB_OBJ": "",
            "POS_VAL_RUB_EXE": str(datetime.datetime.today().year),
            "POS_VAL_RUB_DSE": "",
        },
        "first_year": datetime.datetime.today().year - 6,
        "last_year": datetime.datetime.today().year,
    }

    @staticmethod
    def parse_amiens_content(url, base_url):
        response = requests.get(url=url)
        doc_nums = re.findall(r"(num:)\"([0-9]+)\"", str(response.content))
        for num in doc_nums:
            doc_url = base_url.format(num_doc=num[1], num_page=1, spage=0)
            yield doc_url

    def construct_endpoint_call(self, year, typ, col, qs):
        qs["POS_VAL_RUB_TYP"] = qs["POS_VAL_CTRL_TYP"] = typ
        qs["POS_VAL_RUB_COL"] = qs["POS_VAL_CTRL_COL"] = col
        qs["POS_VAL_RUB_EXE"] = str(year)
        url = self.config["url"] + "?" + urlencode(qs)
        return url

    def parse_response(self, response):
        if response.url in self.SPECIAL_URLS:
            yield from self.parse_special_url(response)
        super().parse_response(response)

    def parse_special_url(self, response):
        """Parse response from the search engine."""
        query_string = self.config["query_string"].copy()
        base_url = self.config["docs_base_url"]
        for year in range(self.config["first_year"], self.config["last_year"] + 1):
            for typology in ["DELIBERATION", "DECISION"]:
                for collectivity in ["AMIENS VILLE", "AMIENS METROPOLE", "CCAS", "EUROPAMIENS"]:
                    url = self.construct_endpoint_call(
                        year, typ=typology, col=collectivity, qs=query_string
                    )
                    for doc_url in self.parse_amiens_content(url, base_url):
                        yield self.yield_special_items(doc_url)

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
