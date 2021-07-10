import logging
import re

import requests
from scrapy.linkextractors import LinkExtractor


class ExtendedLinkExtractor(LinkExtractor):
    """
    Looks into link tag values for crappy JS-embedded links, and skips various URLs

    "Crappy" because those links are activated through JS action, and that's *very*
    bad practice.
    Example: <a href="javascript:window.location='https://example.net';">
    """

    logger = logging.getLogger(__name__)
    jslink_matcher = re.compile(
        r"\s*window\s*\.\s*(open|location)\s*\(\s*(?P<quote>['\"])(.*?)(?P=quote)"
    )

    # See unit tests for real-life example of matching URLs
    # Patterns were stocked in S3 now
    DENY = ()

    ALLOW_DOMAINS = ()

    DENY_DOMAINS = (
        "ademe.fr",
        "anil.org",
        "allocine.fr",
        "ameli.fr",
        "apec.fr",
        "avocats.fr",
        "boamp.fr",
        "caf.fr",
        "cnav.fr",
        "cnil.fr",
        "cnsa.fr",
        "facebook.com",
        "fondsdegarantie.fr",
        "gouvernement.fr",
        "inc-conso.fr",
        "instagram.com",
        "gouv.fr",
        "lassuranceretraite.fr",
        "legislation.fr",
        "linkedin.com",
        "msa.fr",
        "notaires.fr",
        "onac-vg.fr",
        "oui.sncf",
        "parcoursup.fr",
        "pole-emploi.fr",
        "pluginsmarket.com",
        "retraites.fr",
        "senat.fr",
        "service-public.fr",
        "twitter.com",
        "unedic.org",
        "urssaf.fr",
        "voyages-sncf.com",
        "youtube.com",
    )

    def __init__(self, deny_extensions, custom_config):
        self.logger.debug("Instanciation of an ExtendedLinkExtractor")
        deny_domains, deny_patterns, allow_domains, self.post_endpoints = self.get_deny_config(custom_config)
        super().__init__(
            allow=(),
            deny=deny_patterns,
            allow_domains=allow_domains,
            deny_domains=deny_domains,
            restrict_xpaths=(),
            restrict_css=(),
            deny_extensions=deny_extensions,
            restrict_text=None,
            tags=("a", "area", "img", "frame"),
            canonicalize=False,
            unique=True,
            strip=True,
            process_value=self._process_value,
            attrs=("onclick", "href", "src", "data-downloadurl"),
        )

    def _process_value(self, value):
        jslink_match = re.search(self.jslink_matcher, value)
        if jslink_match and len(jslink_match.group(3)) > 0:
            return jslink_match.group(3)
        return value

    def get_deny_config(self, custom_config) -> tuple:
        deny_domains = self.DENY_DOMAINS + tuple(custom_config.get_denied_domain())
        deny_patterns = self.DENY + tuple(custom_config.get_denied_pattern())
        allow_domains = self.ALLOW_DOMAINS + tuple(custom_config.get_allowed_domain())
        post_endpoints = custom_config.get_post_endpoints()
        return deny_domains, deny_patterns, allow_domains, post_endpoints

    @staticmethod
    def is_redirected(url):
        """Detect when an url leads to a redirection and return the redirected url and a flag."""
        r = requests.get(url)
        is_redirected = False
        start_url = url
        for hist in r.history:
            if hist.status_code in [301, 302, 307]:
                is_redirected = True
                start_url = r.url
                break
        return start_url, is_redirected
