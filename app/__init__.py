from typing import Mapping

from flask import Flask, render_template
from dotenv import dotenv_values

from .api import api_init_app
from .cli import cli_init_app


def create_app(test_config: Mapping = None) -> Flask:
    app = Flask(__name__)

    # Config
    configure(app, test_config=test_config)

    # Blueprints
    register_blueprints(app)

    # Extensions
    initialize_extensions(app)

    # Interfaces
    api_init_app(app)
    cli_init_app(app)

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
    app.config.from_object(app.config.get('CONFIG', 'app.config.ProductionConfig'))
    if isinstance(test_config, Mapping):
        app.config.from_mapping(test_config)


def register_blueprints(app: Flask) -> None:
    from .auth.views import bp_auth
    from .main.views import bp_main
    from .orga.views import bp_orga
    from .helper.views import bp_helper
    from .team.views import bp_team

    app.register_blueprint(bp_main)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_orga)
    app.register_blueprint(bp_helper)
    app.register_blueprint(bp_team)


def initialize_extensions(app: Flask) -> None:
    from .models import db, migrate
    from .auth import login_manager, csrf, bcrypt, principal
    from .i18n import babel, locale_selector, timezone_selector

    db.init_app(app)
    migrate.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    bcrypt.init_app(app)
    principal.init_app(app)
    babel.init_app(app, locale_selector=locale_selector, timezone_selector=timezone_selector)

    with app.app_context():
        db.create_all()


def configure_logging(app: Flask) -> None:
    pass


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(401)
    def handle_401(error):
        return render_template('errors/401.jinja2')
