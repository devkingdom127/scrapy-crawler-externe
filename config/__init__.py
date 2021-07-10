import os
import logging

from config import settings

logger = logging.getLogger(__name__)

try:
    env = os.getenv("FLASK_ENV", "development")
    os.environ["FLASK_ENV"] = env

    logger.info("Loading configuration for env=%s", env)
    current_config = getattr(settings, env.capitalize())
except Exception:
    logger.fatal("Cannot find configuration for given env.")
    raise
