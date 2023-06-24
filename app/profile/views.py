from http import HTTPStatus

from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
from flask_babel import gettext as _
from flask_login import login_required

from ..auth import team_permission, guest_permission
from ..models import db, Team

bp_profile = Blueprint('profile', __name__, template_folder='templates', static_folder='static', url_prefix='/profile')


@bp_profile.route('/', methods=['GET'], endpoint='index')
@login_required
@guest_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def index():
    return render_template('my_profile.jinja2')


@bp_profile.route('/team-profile', methods=['GET'], endpoint='team_profile')
@login_required
@team_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def team_profile():
    team_name = request.args.get('team')
    if team_name is None:
        flash(_('No team name provided!'), 'danger')
        return redirect(url_for('main.index'))
    team = db.session.query(Team).where(Team.name == team_name).first()
    if team is None:
        flash(_('The team %(team_name)s was not found!', team_name=team_name), 'danger')
        return redirect(url_for('main.index'))
    return render_template('team_profile.jinja', team=team)


@bp_profile.route('/<string:team_name>', methods=['GET'], endpoint='view')
@login_required
@team_permission.require(HTTPStatus.UNAUTHORIZED)
def index(team_name: str):
    team = db.session.query(Team).where(Team.name == team_name).first()
    if team is None:
        abort(HTTPStatus.NOT_FOUND)
    return render_template('profile.jinja2', team=team)
