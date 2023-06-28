from flask import Blueprint, render_template, abort
from flask_babel import gettext as _

bp_demo = Blueprint('demo', __name__, template_folder='templates', url_prefix='/demo')


@bp_demo.route('/', methods=['GET'], endpoint='index')
def demo():
    return render_template('demo.jinja2')


@bp_demo.route('/<int:error_code>')
def error(error_code: int):
    try:
        abort(error_code)
    except LookupError:
        return _('Not an error code: %(error_code)s', error_code=error_code)
