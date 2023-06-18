from __future__ import annotations

from urllib.parse import urlparse
from enum import Enum, unique

from flask import request, current_app
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


@unique
class RoleName(Enum):
    GUEST = 'guest'
    TEAM = 'team'
    HELPER = 'helper'
    ORGA = 'orga'
    ADMIN = 'admin'


guest_need = RoleNeed(RoleName.GUEST)
team_need = RoleNeed(RoleName.TEAM)
helper_need = RoleNeed(RoleName.HELPER)
orga_need = RoleNeed(RoleName.ORGA)
admin_need = RoleNeed(RoleName.ADMIN)

guest_permission = Permission(guest_need, team_need, helper_need, orga_need, admin_need)
team_permission = Permission(team_need, helper_need, orga_need, admin_need)
helper_permission = Permission(helper_need, orga_need, admin_need)
orga_permission = Permission(orga_need, admin_need)
admin_permission = Permission(admin_need)


@identity_loaded.connect
def on_identity_loaded(sender, identity: Identity):
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
