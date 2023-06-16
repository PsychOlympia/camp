from __future__ import annotations

from urllib.parse import urlparse

from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_principal import Principal, Permission, RoleNeed, identity_loaded, identity_changed
from flask_wtf import CSRFProtect
from flask_babel import gettext as _

from ..models import db, User
from .forms import LoginForm

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Bitte melde dich an, um diese Seite zu sehen!'
csrf = CSRFProtect()
bcrypt = Bcrypt()
principal = Principal()

team_need = RoleNeed('team')
helper_need = RoleNeed('helper')
orga_need = RoleNeed('orga')
admin_need = RoleNeed('admin')

team_permission = Permission(team_need, helper_need, orga_need, admin_need)
helper_permission = Permission(helper_need, orga_need, admin_need)
orga_permission = Permission(orga_need, admin_need)
admin_permission = Permission(admin_need)


def next_url(default: str = None) -> str | None:
    url = request.args.get('next')
    if not url:
        return default
    parsed_url = urlparse(url)
    if not (parsed_url.netloc == '' or parsed_url.netloc == request.host):
        return default
    return parsed_url.geturl()


bp_auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.query(User).where(User.id == user_id).first()


@bp_auth.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.query(User).where(User.username == form.username.data).first()
            if user is not None and bcrypt.check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                # TODO redirect to a personal page after login?
                return redirect(next_url(default=url_for('main.index')))
            else:
                flash(_('Either this user does not exist or the entered password was wrong!'), 'error')
        else:
            flash(_('The form contains invalid data!'), 'error')
    return render_template('login.jinja2', form=form)


@bp_auth.route('/logout', methods=['POST'], endpoint='logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
