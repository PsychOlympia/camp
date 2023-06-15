from typing import Mapping

from flask import Flask
from dotenv import dotenv_values


def create_app(test_config: Mapping = None) -> Flask:
    app = Flask(__name__)

    # Config
    configure(app, test_config=test_config)

    # Blueprints
    register_blueprints(app)

    # Extensions
    initialize_extensions(app)

    # Logging
    configure_logging(app)

    # Application wide error handlers
    register_error_handlers(app)

    return app


def configure(app: Flask, test_config: Mapping) -> None:
    app.jinja_options = {
        'trim_blocks': True,
        'lstrip_blocks': True
    }

    app.config.from_mapping(dotenv_values())
    if isinstance(test_config, Mapping):
        app.config.from_mapping(test_config)


def register_blueprints(app: Flask) -> None:
    from .main.views import bp_main

    app.register_blueprint(bp_main)


def initialize_extensions(app: Flask) -> None:
    pass


def configure_logging(app: Flask) -> None:
    pass


def register_error_handlers(app: Flask) -> None:
    pass
