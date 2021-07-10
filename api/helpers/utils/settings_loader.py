import json
from config.definitions import (allow_cdn,
                                deny_domain, deny_pattern, allow_domain, post_endpoints)
from config.settings import PROJECT_PATH


class SettingsLoader:

    def __init__(self):
        self.custom_config = self.load_config()

    @staticmethod
    def load_config():
        path = PROJECT_PATH / "config" / "crawler_deny_config.json"
        custom_deny_config = json.load(path.open('r'))
        return custom_deny_config

    def get_allowed_cdn(self):
        """Return custom allowed CDN that can be visited because they can host data."""
        return self.custom_config.get(allow_cdn, [])

    def get_allowed_domain(self):
        """Return out of site domains that can be visited because they can host data."""
        return self.custom_config.get(allow_domain, [])

    def get_denied_pattern(self):
        """Return custom denied link patterns (calendar, search engine...)."""
        return self.custom_config.get(deny_pattern, [])

    def get_denied_domain(self):
        """Return domain not to visit (facebook, twitter, météofrance...)."""
        return self.custom_config.get(deny_domain, [])

    def get_post_endpoints(self):
        """Return specific post endpoints to scrap."""
        return self.custom_config.get(post_endpoints, {})
