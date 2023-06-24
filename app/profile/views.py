from http import HTTPStatus

from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
from flask_babel import gettext as _
from flask_login import login_required

from ..auth import team_permission, guest_permission
from ..models import db, Team, User

bp_profile = Blueprint('profile', __name__, template_folder='templates', static_folder='static', url_prefix='/profile')


@bp_profile.route('/', methods=['GET'], endpoint='my_profile')
@login_required
@guest_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def my_profile():
    return render_template('my_profile.jinja2')


@bp_profile.route('/profile', methods=['GET'], endpoint='user')
@login_required
@guest_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def user_profile():
    name = request.args.get('name')
    if name is None:
        flash(_('No name provided!'), 'danger')
        return redirect(url_for('main.index'))
    user = db.session.query(User).where(User.username == name).first()
    if user is None:
        flash(_('The user %(username)s was not found!', username=name), 'danger')
        return redirect(url_for('main.index'))
    return render_template('user_profile.jinja2', user=user)


@bp_profile.route('/<string:team_name>', methods=['GET'], endpoint='team')
@login_required
@team_permission.require(HTTPStatus.UNAUTHORIZED)
def team_profile(team_name: str):
    team = db.session.query(Team).where(Team.name == team_name).first()
    if team is None:
        abort(HTTPStatus.NOT_FOUND)
    return render_template('team_profile.jinja2', team=team)
