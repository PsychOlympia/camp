from __future__ import annotations

from urllib.parse import urlparse
from enum import Enum, unique

from flask import request, current_app, Flask, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_principal import Principal, Permission, RoleNeed, identity_loaded, Identity
from flask_wtf import CSRFProtect
from flask_babel import lazy_gettext as _l

from ..models import db, User

login_manager = LoginManager()
csrf = CSRFProtect()
bcrypt = Bcrypt()
principal = Principal()

login_manager.login_view = 'auth.login'
login_manager.login_message = _l('Please log in to visit this site!')
login_manager.refresh_view = 'auth.login'
login_manager.needs_refresh_message = _l('Please reauthenticate to perform this action.')


@unique
class RoleName(Enum):
    GUEST = 'guest'
    TEAM = 'team'
    HELPER = 'helper'
    ORGA = 'orga'
    ADMIN = 'admin'
    ROOT = 'root'


guest_need = RoleNeed(RoleName.GUEST.value)
team_need = RoleNeed(RoleName.TEAM.value)
helper_need = RoleNeed(RoleName.HELPER.value)
orga_need = RoleNeed(RoleName.ORGA.value)
admin_need = RoleNeed(RoleName.ADMIN.value)
root_need = RoleNeed(RoleName.ADMIN.value)

guest_permission = Permission(guest_need)
team_permission = Permission(team_need)
helper_permission = Permission(helper_need)
orga_permission = Permission(orga_need)
admin_permission = Permission(admin_need)
root_permission = Permission(root_need)


def get_dashboard_url():
    role_names = list(map(lambda role: role.name, current_user.roles))
    if RoleName.ORGA.value in role_names:
        return url_for('orga.index')
    if RoleName.HELPER.value in role_names:
        return url_for('helper.index')
    if RoleName.TEAM.value in role_names:
        return url_for('team.index')
    return url_for('main.index')


@principal.identity_loader
def load_identity_when_session_expires():
    if current_user.is_authenticated:
        return Identity(current_user.id)


@identity_loaded.connect
def on_identity_loaded(sender: Flask, identity: Identity):
    if current_user.is_authenticated:
        identity.provides.add(guest_need)
        for role in current_user.roles:
            if role.name not in map(lambda m: m.value, RoleName.__members__.values()):
                current_app.logger.error(f'Unknown role {role.name} requested by user {current_user.id}')
                continue
            identity.provides.add(RoleNeed(role.name))
    identity.user = current_user


def next_url(default: str = None) -> str | None:
    url = request.form.get('next')
    if not url:
        return default
    parsed_url = urlparse(url)
    if not (parsed_url.netloc == '' or parsed_url.netloc == request.host):
        return default
    return parsed_url.geturl()


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return db.session.query(User).where(User.id == user_id).first()
