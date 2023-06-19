import os

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
Path('app/translations').mkdir(exist_ok=True)


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = (sorted([BABEL_DEFAULT_LOCALE] + os.listdir('app/translations')))
    BABEL_CONFIG_FILE = 'babel.cfg'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    SERVER_NAME = os.environ.get('SERVER_NAME')
