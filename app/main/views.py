from http import HTTPStatus

from flask import Blueprint, render_template, Response
from flask_login import login_required

from ..auth import team_permission
from ..models import db, Team, PointOfInterest, IsMapItem

bp_main = Blueprint('main', __name__, template_folder='templates', static_folder='static')


@bp_main.route('/favicon.ico', defaults={'size': 192}, methods=['GET'])
@bp_main.route('/favicon-<int:size>.png', methods=['GET'], endpoint='favicon')
def favicon(size: int):
    return bp_main.send_static_file(f'favicon-{size}.png')


@bp_main.route('/robots.txt', methods=['GET'])
def robots():
    return Response(response='User-agent: *\nDisallow: /', mimetype='text/plain')


@bp_main.route('/', methods=['GET'], endpoint='index')
def index():
    return render_template('index.jinja2')


@bp_main.route('/team-map', methods=['GET'], endpoint='team_map')
@login_required
@team_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def team_map():
    map_items: list[IsMapItem] = (
        db.session.query(Team).where(Team._country_location != None).all()  # noqa
        + db.session.query(PointOfInterest).where(PointOfInterest._country_location != None).all()  # noqa
    )
    return render_template('team_map.jinja2', map_items=map_items)


@bp_main.route('/camp-map', methods=['GET'], endpoint='camp_map')
@login_required
@team_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def camp_map():
    map_items: list[IsMapItem] = (
        db.session.query(Team).where(Team._camp_location != None).all()  # noqa
        + db.session.query(PointOfInterest).where(PointOfInterest._camp_location != None).all()  # noqa
    )
    return render_template('camp_map.jinja2', map_items=map_items)
