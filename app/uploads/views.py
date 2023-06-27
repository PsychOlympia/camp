from http import HTTPStatus
from pathlib import Path

from flask import Blueprint, send_from_directory, current_app
from flask_login import login_required

from app.auth import guest_permission

bp_uploads = Blueprint('upload', __name__, url_prefix='/uploads', static_folder='files')


def get_user_upload_directory() -> Path:
    path = Path(bp_uploads.static_folder) / 'users'
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_team_upload_directory() -> Path:
    path = Path(bp_uploads.static_folder) / 'teams'
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_poi_upload_directory() -> Path:
    path = Path(bp_uploads.static_folder) / 'pois'
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_temp_upload_directory() -> Path:
    path = Path(bp_uploads.static_folder) / 'temp'
    path.mkdir(parents=True, exist_ok=True)
    return path


@bp_uploads.route('/users/<string:filename>', methods=['GET'], endpoint='user')
@login_required
@guest_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def user_upload(filename: str):
    return send_from_directory(
        directory=get_user_upload_directory().relative_to(Path(current_app.root_path)),
        path=filename
    )


@bp_uploads.route('/teams/<string:filename>', methods=['GET'], endpoint='team')
@login_required
@guest_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def team_upload(filename: str):
    return send_from_directory(
        directory=get_team_upload_directory().relative_to(Path(current_app.root_path)),
        path=filename
    )


@bp_uploads.route('/point-of-interest/<string:filename>', methods=['GET'], endpoint='pointofinterest')
@login_required
@guest_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def poi_upload(filename: str):
    return send_from_directory(
        directory=get_poi_upload_directory().relative_to(Path(current_app.root_path)),
        path=filename
    )


@bp_uploads.route('/temp/<string:filename>', methods=['GET'], endpoint='temp')
@login_required
@guest_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def temp_upload(filename: str):
    return send_from_directory(
        directory=get_temp_upload_directory().relative_to(Path(current_app.root_path)),
        path=filename
    )
