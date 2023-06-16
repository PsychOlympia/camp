from flask import Blueprint

from ..auth import csrf

bp_api = Blueprint('api', __name__, url_prefix='/api')
csrf.exempt(bp_api)
