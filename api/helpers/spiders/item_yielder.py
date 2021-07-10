import logging
from pathlib import Path
from typing import Dict

from api.models.admin_doc_item import AdminDocItem
from scrapy.http import Response

from config.definitions import Cst, output_urls
from config.settings import PROJECT_PATH


class ItemYielder:
    """
    This class is responsible for the generation of instances of AdminDocItem
    """
    DEFAULT_MIME_TYPES = ['application/octet-stream', 'application/oct-stream']
    logger = logging.getLogger(__name__)

    def __init__(self, start_url: str, locations: list, operation_uid: str, accepted_mime_types: Dict):

        # for export
        self.locations = locations
        self.dataProvider = start_url
        self.operation_uid = operation_uid
        self.output_file = PROJECT_PATH / "output" / output_urls
        self.output_file.unlink(missing_ok=True)

        # for validation
        self.accepted_mime_types = accepted_mime_types

    def save_line(self, url):
        with self.output_file.open('a') as f:
            f.write(url + '\n')

    def from_response(self, response: Response, spider):

        content_type_header, is_accepted = self.get_content_type(response)
        if is_accepted:
            self.logger.debug('Found an accepted document: %s', response.url)

            spider.add_to_collected_url(response.url)
            self.save_line(response.url)
            yield AdminDocItem(
                url=response.url,
                responseMimeContentType=content_type_header,
                locations=self.locations,
                dataProvider=self.dataProvider,
                operationId=self.operation_uid
            )

        else:
            self.logger.debug('Skipping a response with content type %s: %s', content_type_header, response.url)

    def get_content_type(self, response: Response) -> tuple:
        """
        This fetches the content type of the current HTTP response, and
        whether this is an accepted content type.
        """
        binary_content_type = response.headers.get('content-type', None)
        content_type_header = binary_content_type.decode('utf-8')
        is_accepted = self.is_content_type_accepted(content_type_header, self.accepted_mime_types.values())
        if is_accepted is not True and self.is_content_type_accepted(content_type_header, self.DEFAULT_MIME_TYPES):
            is_accepted = self.with_extension_accepted(response)
        return content_type_header, is_accepted

    @staticmethod
    def with_extension_accepted(response: Response) -> bool:
        """
        This check if the current HTTP response have extension_accepted.
        """
        if Cst.PDF_EXTENSION in response.url.split('/')[-1]:
            return True
        else:
            try:
                content_disposition_header = response.headers.get('content-disposition', None).decode('utf-8')
                return Cst.PDF_EXTENSION in content_disposition_header
            except AttributeError:
                return False

    @staticmethod
    def is_content_type_accepted(content_type_header: str, accepted_mime_types: any):
        return any(content_type in content_type_header for content_type in accepted_mime_types)
