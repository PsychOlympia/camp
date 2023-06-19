from flask import Blueprint, redirect, url_for, request, render_template, flash, current_app
from flask_login import login_user, login_required, logout_user
from flask_principal import Identity, identity_changed, AnonymousIdentity
from flask_babel import gettext as _

from ..models import db, User
from .forms import LoginForm
from . import bcrypt, next_url, RoleName

bp_auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')


@bp_auth.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.query(User).where(User.username == form.username.data).first()
            if user is not None and bcrypt.check_password_hash(user.password_hash, form.password.data):
                login_user(user, remember=True)
                identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))  # noqa
                default_url = url_for('main.index')
                user_role_names = map(lambda role: role.name, user.roles)
                if RoleName.TEAM.value in user_role_names:
                    default_url = url_for('team.index')
                if RoleName.HELPER.value in user_role_names:
                    default_url = url_for('helper.index')
                if RoleName.ORGA.value in user_role_names:
                    default_url = url_for('orga.index')
                return redirect(next_url(default=default_url))
            else:
                flash(_('Either this user does not exist or the entered password was wrong!'), 'danger')
        else:
            flash(_('The form contains invalid data!'), 'danger')
    return render_template('login.jinja2', form=form)


@bp_auth.route('/logout', methods=['POST'], endpoint='logout')
@login_required
def logout():
    logout_user()
    identity_changed.send(current_app, identity=AnonymousIdentity())
    return redirect(url_for('main.index'))
