from __future__ import annotations

from urllib.parse import urlparse

from flask import request
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_principal import Principal, Permission, RoleNeed, identity_loaded, Identity
from flask_wtf import CSRFProtect
from flask_babel import lazy_gettext as _l

from ..models import db, User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = _l('Please log in to visit this site!')
csrf = CSRFProtect()
bcrypt = Bcrypt()
principal = Principal()

guest_need = RoleNeed('guest')
team_need = RoleNeed('team')
helper_need = RoleNeed('helper')
orga_need = RoleNeed('orga')
admin_need = RoleNeed('admin')

guest_permission = Permission(guest_need, team_need, helper_need, orga_need, admin_need)
team_permission = Permission(team_need, helper_need, orga_need, admin_need)
helper_permission = Permission(helper_need, orga_need, admin_need)
orga_permission = Permission(orga_need, admin_need)
admin_permission = Permission(admin_need)


@identity_loaded.connect
def on_identity_loaded(sender, identity: Identity):
    # Update the roles that a user can provide
    if current_user.is_authenticated:
        identity.provides.add(guest_need)
        # TODO CRITICAL User.roles
        """
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))
        """
    # Save the user somewhere, so we only look it up once
    identity.user = current_user


def next_url(default: str = None) -> str | None:
    url = request.args.get('next')
    if not url:
        return default
    parsed_url = urlparse(url)
    if not (parsed_url.netloc == '' or parsed_url.netloc == request.host):
        return default
    return parsed_url.geturl()


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.query(User).where(User.id == user_id).first()
