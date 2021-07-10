import json

import boto3
from scrapy.spidermiddlewares.httperror import HttpError, HttpErrorMiddleware

from api.models.input_message import InputMessage
from config import definitions

sqs_client = boto3.client("sqs", region_name=definitions.get_output_queue_region())


class SQSPushHttpError(HttpErrorMiddleware):

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, HttpError):
            self.sqs_push_error(response, exception)

        super().process_spider_exception(response, exception, spider)

    def sqs_push_error(self, response, exception):
        pass

    @staticmethod
    def process_message(response, exception) -> tuple:
        body = InputMessage.body.copy()
        body["crawler_options"]["start_url"] = response.url
        body["retry"] = body.get("retry", 0) + 1
        attributes = {
            "Error":
                {
                    "DataType": "String",
                    "StringValue": f"{repr(exception)} with status {response.status}"
                }
        }

        return json.dumps(body), attributes
