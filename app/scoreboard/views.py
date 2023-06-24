from http import HTTPStatus

from flask import Blueprint, render_template
from flask_login import login_required

from app.auth import team_permission

bp_scoreboard = Blueprint(
    'scoreboard', __name__, template_folder='templates', static_folder='static', url_prefix='/scoreboard'
)


@bp_scoreboard.route('/', methods=['GET'], endpoint='index')
@login_required
@team_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def index():
    return render_template('scoreboard.jinja2')
