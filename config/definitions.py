import os

ADMINDOC_CRAWLER_PENSIEVE_DEFAULT_URL = 'http://127.0.0.1:8000'
ADMINDOC_CRAWLER_OUTPUT_QUEUE_DEFAULT_REGION = 'eu-west-3'
ADMINDOC_CRAWLER_DEFAULT_ENV = 'development'
ADMINDOC_CRAWLER_DEFAULT_S3_CONFIG = 's3-admindoc-config'
ADMINDOC_CRAWLER_DEFAULT_TIMEOUT_ALERT = 3600
ADMINDOC_CRAWLER_DEPTH_LIMIT_DEFAULT = 0
ADMINDOC_CRAWLER_RETRY_TIMES_DEFAULT = 2
ADMINDOC_CRAWLER_DOWNLOAD_TIMEOUT_DEFAULT = 180
ADMINDOC_CRAWLER_CLOSESPIDER_TIMEOUT_DEFAULT = 0
ADMINDOC_CRAWLER_DOWNLOAD_DELAY_DEFAULT = 0
ADMINDOC_CRAWLER_CONCURRENT_REQUESTS_DEFAULT = 16
SLEEP_DELAY = 10
DOWNLOAD_MAXSIZE = 104857600  # 100MB


def get_pensieve_url():
    return os.getenv('ADMINDOC_CRAWLER_PENSIEVE_URL', ADMINDOC_CRAWLER_PENSIEVE_DEFAULT_URL)


def get_output_queue_region():
    return os.getenv('ADMINDOC_CRAWLER_OUTPUT_QUEUE_REGION', ADMINDOC_CRAWLER_OUTPUT_QUEUE_DEFAULT_REGION)


def get_output_queue_url():
    return os.getenv('ADMINDOC_CRAWLER_OUTPUT_QUEUE_URL', None)


def get_error_queue_url():
    return os.getenv('ADMINDOC_CRAWLER_ERROR_QUEUE_URL', None)


def get_env():
    return os.getenv('ADMINDOC_CRAWLER_ENV', ADMINDOC_CRAWLER_DEFAULT_ENV)


def get_rollbar_token():
    return os.getenv('ROLLBAR_TOKEN', None)


def get_max_duration_crawler_alert():
    return os.getenv('DURATION_CRAWLER_ALERT', ADMINDOC_CRAWLER_DEFAULT_TIMEOUT_ALERT)


# https://docs.scrapy.org/en/latest/topics/settings.html?highlight=DEPTH_LIMIT#depth-limit
def get_depth_limit():
    return os.getenv('ADMINDOC_CRAWLER_DEPTH_LIMIT', ADMINDOC_CRAWLER_DEPTH_LIMIT_DEFAULT)


# https://docs.scrapy.org/en/latest/topics/downloader-middleware.html?highlight=RETRY_TIMES#retry-times
def get_retry_times():
    return os.getenv('ADMINDOC_CRAWLER_RETRY_TIMES', ADMINDOC_CRAWLER_RETRY_TIMES_DEFAULT)


# https://docs.scrapy.org/en/latest/topics/settings.html?highlight=DOWNLOAD_TIMEOUT#download-timeout
def get_download_timeout():
    return os.getenv('ADMINDOC_CRAWLER_DOWNLOAD_TIMEOUT', ADMINDOC_CRAWLER_DOWNLOAD_TIMEOUT_DEFAULT)


# https://docs.scrapy.org/en/latest/topics/extensions.html?highlight=CLOSESPIDER#std-setting-CLOSESPIDER_TIMEOUT
def get_close_spider_timeout():
    return os.getenv('ADMINDOC_CRAWLER_CLOSESPIDER_TIMEOUT', ADMINDOC_CRAWLER_CLOSESPIDER_TIMEOUT_DEFAULT)


# https://docs.scrapy.org/en/latest/topics/settings.html?highlight=DOWNLOAD_DELAY#download-delay
def get_download_delay():
    return os.getenv('ADMINDOC_CRAWLER_DOWNLOAD_DELAY', ADMINDOC_CRAWLER_DOWNLOAD_DELAY_DEFAULT)


# https://docs.scrapy.org/en/latest/topics/settings.html?highlight=CONCURRENT_REQUESTS#concurrent-requests
def get_concurrent_requests():
    return os.getenv('ADMINDOC_CRAWLER_CONCURRENT_REQUESTS', ADMINDOC_CRAWLER_CONCURRENT_REQUESTS_DEFAULT)


def get_s3_config_path():
    return os.getenv('ADMINDOC_CRAWLER_S3_CONFIG', ADMINDOC_CRAWLER_DEFAULT_S3_CONFIG)


class Cst:
    PUBLISHER = "publisher"
    PDF_EXTENSION = ".pdf"
    JSON_CONTENT_TYPE = "application/json"
    PDF_CONTENT_TYPE = "application/pdf"


deny_config_path = 'crawler_deny_config.json'
deny_domain = "denyDomain"
deny_pattern = "denyPattern"
allow_domain = "allowDomain"
allow_cdn = "allowCDN"
post_endpoints = "postEndpoints"
visited_urls = "visited_urls.txt"
output_urls = "output_urls.txt"
