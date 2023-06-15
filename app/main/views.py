from flask import Blueprint, render_template, Response

bp_main = Blueprint('main', __name__, template_folder='templates', static_folder='static')


@bp_main.route('/', methods=['GET'], endpoint='index')
def index():
    return render_template('index.jinja2')


@bp_main.route('/favicon.ico', defaults={'size': 192}, methods=['GET'])
@bp_main.route('/favicon-<int:size>.png', methods=['GET'], endpoint='favicon')
def favicon(size: int):
    return bp_main.send_static_file(f'favicon-{size}.png')


@bp_main.route('/robots.txt', methods=['GET'])
def robots():
    return Response(response='User-agent: *\nDisallow: /', mimetype='text/plain')
