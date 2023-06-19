from http import HTTPStatus

from flask import Blueprint, render_template
from flask_login import login_required

from ..auth import helper_permission

bp_helper = Blueprint('helper', __name__, template_folder='templates', static_folder='static', url_prefix='/helper')


@bp_helper.route('/', methods=['GET'], endpoint='index')
@helper_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
@login_required
def index():
    return render_template('helper_dashboard.jinja2')
