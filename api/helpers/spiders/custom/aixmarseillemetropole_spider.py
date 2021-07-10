from api.helpers.spiders.admin_doc_spider import AdminDocSpider


class AixMarseilleParser(AdminDocSpider):
    """
    Class to parse Amiens Website. In particular, this class is designed to retrieve documents
    from the search engine.
    """

    SPECIAL_URLS = ["https://www.ampmetropole.fr/les-seances"]
    DELIB_URL = "https://deliberations.ampmetropole.fr"
    METROPOLE_URL = "https://www.ampmetropole.fr"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [self.METROPOLE_URL, self.DELIB_URL]
