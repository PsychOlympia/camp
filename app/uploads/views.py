from pathlib import Path

from flask import Blueprint, send_from_directory
from flask_login import login_required


bp_uploads = Blueprint('upload', __name__, url_prefix='/uploads', static_folder='files')


def get_user_upload_directory() -> Path:
    return Path(bp_uploads.static_folder) / 'users'


def get_team_upload_directory() -> Path:
    return Path(bp_uploads.static_folder) / 'teams'


@bp_uploads.route('/users/<string:filename>', methods=['GET'], endpoint='user')
@login_required
def user_upload(filename: str):
    user_upload_directory = get_user_upload_directory()
    user_upload_directory.mkdir(parents=True, exist_ok=True)
    return send_from_directory(directory=user_upload_directory, path=filename)


@bp_uploads.route('/teams/<string:filename>', methods=['GET'], endpoint='team')
@login_required
def team_upload(filename: str):
    team_upload_directory = get_team_upload_directory()
    team_upload_directory.mkdir(parents=True, exist_ok=True)
    return send_from_directory(directory=team_upload_directory, path=filename)
