from http import HTTPStatus
from typing import Mapping

from flask import Flask, render_template, flash, request, url_for, redirect
from flask_principal import PermissionDenied
from flask_babel import gettext as _
from dotenv import dotenv_values

from .api import api_init_app
from .auth import get_dashboard_url
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
    # jinja options
    app.jinja_options = {
        'trim_blocks': True,
        'lstrip_blocks': True
    }

    # jinja functions
    app.add_template_global(get_dashboard_url, 'dashboard_url')

    # jinja variables
    @app.context_processor
    def global_variables():
        from .i18n import locale_selector
        return dict(lang=locale_selector())

    # config
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
    from .infopanel.views import bp_infopanel
    from .profile.views import bp_profile
    from .settings.views import bp_profile_settings
    from .scoreboard.views import bp_scoreboard

    app.register_blueprint(bp_main)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_orga)
    app.register_blueprint(bp_helper)
    app.register_blueprint(bp_team)
    app.register_blueprint(bp_infopanel)
    app.register_blueprint(bp_profile)
    app.register_blueprint(bp_profile_settings)
    app.register_blueprint(bp_scoreboard)


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
    @app.errorhandler(PermissionDenied)
    @app.errorhandler(HTTPStatus.UNAUTHORIZED)
    def handle_401(error):
        return render_template('errors/401.jinja2')

    @app.errorhandler(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
    def too_large(e):
        flash(_('This file is too large!'), 'danger')
        return redirect(url_for(request.endpoint))
