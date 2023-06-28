from http import HTTPStatus

from flask import Blueprint, render_template
from flask_login import login_required

from ..auth import team_permission
from ..development import experimental

bp_team = Blueprint('team', __name__, template_folder='templates', static_folder='static', url_prefix='/team')


@bp_team.route('/', methods=['GET'], endpoint='index')
@login_required
@team_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def index():
    return render_template('team_dashboard.jinja2')


@bp_team.route('/my-events', methods=['GET'], endpoint='my_events')
@login_required
@team_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
@experimental
def my_events():
    return render_template('my_team_events.jinja2')
