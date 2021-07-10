import logging
from datetime import datetime

from api.models.input_message import InputMessage
from api.services.scrapy import admin_doc_scraper


class Crawler:
    logger = logging.getLogger(__name__)

    @staticmethod
    def _generate_uid(user):
        """
        To generate a uid that respect collect_operation uid pattern
        Ex : 02012020_11h12_fbruniaux
        """
        now = datetime.now()
        today = now.strftime("%d%m%Y")
        current_time = now.strftime("%Hh%Mm%Ss%f")

        uid = f'{today}_{current_time}_{user}'
        return uid

    @staticmethod
    def run(parameters) -> str:
        InputMessage.body = parameters
        start_url, locations, user = InputMessage.get_options()
        operation_uid = Crawler._generate_uid(user)

        Crawler.logger.info(f'About to start crawler operation {operation_uid} with {start_url}')
        task = admin_doc_scraper(
            start_url=start_url,
            locations=locations,
            operation_uid=operation_uid
        )
        Crawler.logger.info(f'Started crawler operation {operation_uid} (internal Celery id: {task})')

        return operation_uid
