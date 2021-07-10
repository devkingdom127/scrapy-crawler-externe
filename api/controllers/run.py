from http import HTTPStatus
from logging import getLogger

from api.models.error import Error
from api.services.crawler import Crawler


# POST /run
def post(body):
    logger = getLogger(__name__)
    try:
        logger.error("Received body: %s" % body)
        task_id = Crawler.run(body)
        output = {
            "task-id": task_id
        }

    except Exception as e:
        logger.error("Failure: %s" % e)
        return Error.internal_error(e).response()

    return (
        output,
        HTTPStatus.OK
    )
