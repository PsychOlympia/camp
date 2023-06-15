from typing import Mapping

from flask import Flask
from dotenv import dotenv_values

from .config import ProductionConfig, DevelopmentConfig, TestConfig


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
    app.config.from_object(ProductionConfig)
    if isinstance(test_config, Mapping):
        app.config.from_mapping(test_config)


def register_blueprints(app: Flask) -> None:
    from .main.views import bp_main
    from .auth import bp_auth

    app.register_blueprint(bp_main)
    app.register_blueprint(bp_auth)


def initialize_extensions(app: Flask) -> None:
    from .models import db, migrate

    db.init_app(app)
    migrate.init_app(app)

    with app.app_context():
        db.create_all()


def configure_logging(app: Flask) -> None:
    pass


def register_error_handlers(app: Flask) -> None:
    pass
