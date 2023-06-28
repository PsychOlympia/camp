from flask import Blueprint

bp_sponsored = Blueprint(
    'sponsored', __name__, template_folder='templates', static_folder='static', url_prefix='/sponsored'
)

