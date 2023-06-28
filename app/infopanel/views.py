from http import HTTPStatus

from flask import Blueprint, render_template
from flask_login import login_required

from ..auth import guest_permission
from ..development import experimental

bp_infopanel = Blueprint(
    'infopanel', __name__, template_folder='templates', static_folder='static', url_prefix='/infopanel'
)


@bp_infopanel.route('/', methods=['GET'], endpoint='index')
@login_required
@guest_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)  # TODO who should have access (can view camp?)
@experimental
def index():
    return render_template('infopanel.jinja2')


@bp_infopanel.route('/weather', methods=['GET'], endpoint='weather')
@login_required
@guest_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
@experimental
def weather():
    return render_template('weather.jinja2')
