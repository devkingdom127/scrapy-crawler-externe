import os

from pathlib import Path

PROJECT_PATH = Path(__file__).parent.parent.resolve()


class Config(object):
    SERVER_NAME = '0.0.0.0'
    SERVER_PORT = '9090'
    DEBUG = False
    TESTING = False


class Development(Config):
    SERVER_NAME = '127.0.0.1'
    SERVER_PORT = '9090'
    FLASK_ENV = 'development'
    DEBUG = True


class Staging(Config):
    FLASK_ENV = 'staging'
    DEBUG = True


class Production(Config):
    FLASK_ENV = 'production'
