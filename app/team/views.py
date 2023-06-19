from http import HTTPStatus

from flask import Blueprint, render_template
from flask_login import login_required

from ..auth import team_permission

bp_team = Blueprint('team', __name__, template_folder='templates', static_folder='static', url_prefix='/team')


@bp_team.route('/', methods=['GET'], endpoint='index')
@team_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
@login_required
def index():
    return render_template('team_dashboard.jinja2')
