from functools import partial

import rollbar
import rollbar.contrib.flask
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden, NotFound

from config import current_config
from config.connexion import application
from config.connexion import logger
from config.settings import PROJECT_PATH


@application.app.before_first_request
def log_error():
    """init rollbar module"""
    application.add_error_handler(Exception, lambda e: logger.error(e))

    ignored_exceptions = map(
        lambda x: (x, 'ignored'),
        [BadRequest, Unauthorized, Forbidden, NotFound]
    )

    rollbar.init(
        "xxxxxx",
        current_config.FLASK_ENV,
        root=PROJECT_PATH,
        allow_logging_basic_config=False,
        exception_level_filters=ignored_exceptions)

    application.add_error_handler(
        Exception,
        partial(rollbar.contrib.flask.report_exception, application)
    )


# run the app.
if __name__ == "__main__":
    """Represent main entry of the program."""
    application.run(
        host=current_config.SERVER_NAME,
        port=current_config.SERVER_PORT,
        debug=current_config.DEBUG
    )
