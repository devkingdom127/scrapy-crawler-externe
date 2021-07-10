from rollbar import init, report_message
from config.definitions import get_env as env
from config.definitions import get_rollbar_token


def init_rollbar(start_url):
    """Instantiate a rollbar talker, only if ROLLBAR_TOKEN os env if found."""

    key = get_rollbar_token()
    if key is None:
        return

    init(key, env)
    report_message(f'Initiate admin_doc collect v2 from start_url {start_url}', level='info')
