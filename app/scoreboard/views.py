from http import HTTPStatus

from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import desc

from ..auth import team_permission
from ..models import db, Scoreboard

bp_scoreboard = Blueprint(
    'scoreboard', __name__, template_folder='templates', static_folder='static', url_prefix='/scoreboard'
)


@bp_scoreboard.route('/', methods=['GET'], endpoint='index')
@login_required
@team_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def index():
    latest_round = db.session.query(Scoreboard).order_by(desc(Scoreboard.round)).first()
    if latest_round is None:
        entries = []
    else:
        entries = latest_round.entries
    return render_template('scoreboard.jinja2', entries=entries)
