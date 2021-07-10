import logging.config
from pathlib import Path

import connexion
from connexion.resolver import RestyResolver
from prance import ResolvingParser

logging_conf_path = Path(__file__).parent / "logging.conf"
logging.config.fileConfig(logging_conf_path)


def get_bundled_specs(main_file: Path) -> dict:
    parser = ResolvingParser(
        str(main_file.absolute()),
        lazy=True,
        backend='openapi-spec-validator'
    )
    parser.parse()

    assert parser.valid, 'Invalid OpenAPI specification!'

    return parser.specification


SPEC_PATH = Path(__file__).parent.parent / 'contracts' / 'spec.yaml'

options = {'swagger_url': '/'}
application = connexion.App(__name__, options=options)
application.app.url_map.strict_slashes = False
application.add_api(
    get_bundled_specs(SPEC_PATH),
    validate_responses=True,
    strict_validation=True,
    resolver=RestyResolver('api.controllers')
)
logger = application.app.logger
