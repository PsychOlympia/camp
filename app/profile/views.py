from http import HTTPStatus

from flask import Blueprint, render_template, abort

from ..models import db, Team

bp_profile = Blueprint('profile', __name__, template_folder='templates', static_folder='static', url_prefix='/profile')


@bp_profile.route('/<string:team_name>', methods=['GET'], endpoint='index')
def index(team_name: str):
    team = db.session.query(Team).where(Team.name == team_name).first()
    if team is None:
        abort(HTTPStatus.NOT_FOUND)
    return render_template('profile.jinja2', team=team)
