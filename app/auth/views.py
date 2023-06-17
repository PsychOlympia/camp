from flask import Blueprint, redirect, url_for, request, render_template, flash, current_app
from flask_login import login_user, login_required, logout_user
from flask_principal import Identity, identity_changed, AnonymousIdentity
from flask_babel import gettext as _

from ..models import db, User
from .forms import LoginForm
from . import bcrypt, next_url

bp_auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')


@bp_auth.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.query(User).where(User.username == form.username.data).first()
            if user is not None and bcrypt.check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                # identity_changed.send(current_app, identity=Identity(user.roles))  # TODO CRITICAL User.roles
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
    identity_changed.send(current_app, identity=AnonymousIdentity())
    return redirect(url_for('main.index'))
