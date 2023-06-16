from flask import Blueprint
from flask_login import LoginManager
from flask_principal import Principal, Permission, RoleNeed

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Bitte melde dich an, um diese Seite zu sehen!'

bp_auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')
