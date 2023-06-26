import os

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
Path('app/translations').mkdir(exist_ok=True)
Path('app/static/uploads').mkdir(exist_ok=True ,parents=True)


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = (sorted([BABEL_DEFAULT_LOCALE] + os.listdir('app/translations')))
    BABEL_CONFIG_FILE = 'babel.cfg'
    MAP_ICON_SIZE = 32
    UPLOAD_PATH = Path('app/static/uploads')
    MAX_CONTENT_LENGTH = 1 * 1024 ** 2


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    SERVER_NAME = os.environ.get('SERVER_NAME')
