from datetime import date, timedelta

from flask import Blueprint, Flask, request

from .weather import Weather
from ..auth import csrf

bp_api = Blueprint('api', __name__, url_prefix='/api')
csrf.exempt(bp_api)

weather_bp = Blueprint('weather', __name__, url_prefix='/weather')
bp_api.register_blueprint(weather_bp)

weather = Weather(location=(0.0, 0.0))


def api_init_app(app: Flask) -> None:
    app.register_blueprint(bp_api)
    weather.location_name = app.config['CAMP_LOCATION_NAME']
    weather.location = (float(app.config['CAMP_LOCATION_LAT']), float(app.config['CAMP_LOCATION_LON']))


@weather_bp.route('/nowcast', methods=['GET'], endpoint='nowcast')
def nowcast():
    return weather.current().get('weather', {})


@weather_bp.route('/forecast', methods=['GET'], endpoint='forecast')
def forecast():
    start = date.today()
    return weather.forecast(
        start=start,
        end=start + timedelta(days=float(request.args.get('days', 0)) + 1)
    ).get('weather', [])
