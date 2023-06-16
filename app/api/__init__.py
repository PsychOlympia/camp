from flask import Blueprint, Flask

from ..auth import csrf

bp_api = Blueprint('api', __name__, url_prefix='/api')
csrf.exempt(bp_api)


def api_init_app(app: Flask) -> None:
    app.register_blueprint(bp_api)
