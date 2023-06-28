from flask import Blueprint, render_template, abort

bp_demo = Blueprint('demo', __name__, template_folder='templates', url_prefix='/demo')


@bp_demo.route('/', methods=['GET'], endpoint='index')
def demo():
    return render_template('demo.jinja2')


@bp_demo.route('/500')
def error_500():
    abort(500)
