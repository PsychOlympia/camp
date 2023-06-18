from http import HTTPStatus

from flask import Blueprint, render_template
from flask_login import login_required

from ..auth import orga_permission

bp_orga = Blueprint('orga', __name__, template_folder='templates', static_folder='static', url_prefix='/orga')


@bp_orga.route('/', methods=['GET'], endpoint='index')
@orga_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
@login_required
def index():
    return render_template('orga_dashboard.jinja2')
