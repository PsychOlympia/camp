import hashlib
from http import HTTPStatus
from pathlib import Path

from flask import Blueprint, request, redirect, url_for, render_template, flash, abort, current_app
from flask_login import login_required, current_user
from flask_principal import PermissionDenied
from flask_babel import gettext as _

from .forms import MapLocationForm, FileUploadForm
from ..auth import orga_permission, guest_permission
from ..models import db, Team, PointOfInterest, User
from ..uploads import get_user_upload_directory

bp_profile_settings = Blueprint(
    'settings', __name__, template_folder='templates', static_folder='static', url_prefix='/settings'
)


@bp_profile_settings.route('/user', methods=['GET'], endpoint='user')
@login_required
@guest_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def user_settings():
    file_upload_form = FileUploadForm()
    return render_template('user_settings.jinja2', file_upload_form=file_upload_form)


@bp_profile_settings.route('/user/update-profile-picture', methods=['GET', 'POST'], endpoint='update_user_profile_picture')
@login_required
@guest_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def update_user_profile_picture():
    if request.method == 'GET':
        return redirect(url_for('.user'))

    file_upload_form = FileUploadForm()

    if file_upload_form.file_upload.data is None:
        flash(_('No file provided!'), 'danger')
        return redirect(url_for('.user'))

    data = file_upload_form.file_upload.data.stream.read()
    content_hash = hashlib.sha3_256(data).hexdigest()
    filename = f'{content_hash}{Path(file_upload_form.file_upload.data.filename).suffix}'
    with open(get_user_upload_directory() / filename, mode='wb') as f:
        f.write(data)
    current_user.logo = filename
    db.session.commit()
    flash(_('Profile picture updated!'), 'success')
    return redirect(url_for('.user'))


@bp_profile_settings.route('/user/delete-profile-picture', methods=['POST'], endpoint='delete_user_profile_picture')
@login_required
@guest_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def delete_user_profile_picture():
    if current_user.logo is None:
        flash(_("You don't have a profile picture!"), 'danger')
        return redirect(url_for('.user'))
    if len(db.session.query(User).where(User.logo == current_user.logo).all()) <= 1:  # no refs remaining
        (get_user_upload_directory() / current_user.logo).unlink(missing_ok=True)
    current_user.logo = None
    db.session.commit()
    flash(_('Profile picture deleted'), 'success')
    return redirect(url_for('.user'))


@bp_profile_settings.route('/team', methods=['GET'], endpoint='team')
@login_required
@guest_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def team_settings():
    if current_user.team is None:
        flash(_('You are not part of a team!'))
        return redirect(url_for('main.index'))
    return render_template('team_settings.jinja2')


@bp_profile_settings.route(
    '/set-camp-location', methods=['GET', 'POST'], endpoint='set_camp_location',
    defaults={'place': 'camp'}
)
@bp_profile_settings.route(
    '/set-country-location', methods=['GET', 'POST'], endpoint='set_country_location',
    defaults={'place': 'country'}
)
@login_required
def set_location(place: str):  # noqa
    place = place.lower()
    if place not in ('country', 'camp'):
        abort(HTTPStatus.NOT_FOUND)

    form = MapLocationForm()
    form.item_name.data = request.values.get('item_name')
    form.item_type.data = request.values.get('item_type')

    if form.item_type.data is None or form.item_name.data is None:  # noqa duplicate lines
        flash(_('Invalid form data!'), 'danger')
        return redirect(url_for('main.index'))

    if form.item_type.data not in ('team', 'poi'):
        flash(_('Unknown item type!'), 'danger')
        return redirect(url_for('main.index'))

    item = (
        db.session.query(Team)
        .where(Team.name == form.item_name.data)
        .first()
        if form.item_type.data == 'team'
        else db.session.query(PointOfInterest)
        .where(PointOfInterest.name == form.item_name.data)
        .first()
    )

    if item is None:
        flash(_('Item not found!'), 'danger')
        return redirect(url_for('main.index'))

    if type(item) is Team and current_user.team != item:
        raise PermissionDenied()
    if type(item) is PointOfInterest and not orga_permission.can():
        raise PermissionDenied()

    if request.method == 'POST':
        if form.validate_on_submit():
            if place == 'country':
                item.country_location = (form.latitude.data, form.longitude.data)
            else:
                item.camp_location = (form.latitude.data, form.longitude.data)
            db.session.commit()
            flash(_('Postion updated!'), 'success')
            if form.item_type.data == 'team':
                return redirect(url_for('settings.team', team_name=form.item_name.data))
            else:
                return redirect(url_for('main.index'))  # TODO adjust
        flash(_('Invalid form data!'), 'danger')
    if place == 'country':
        form.latitude.data, form.longitude.data = (
            (None, None) if item.country_location is None else item.country_location
        )
        return render_template(
            'set_country_location_map.jinja2', item=item, form=form
        )
    else:
        form.latitude.data, form.longitude.data = ((None, None) if item.camp_location is None else item.camp_location)
        return render_template(
            'set_camp_location_map.jinja2', item=item, form=form
        )


@bp_profile_settings.route(
    '/delete-camp-location', methods=['POST'], endpoint='delete_camp_location', defaults={'place': 'camp'}
)
@bp_profile_settings.route(
    '/delete-country-location', methods=['POST'], endpoint='delete_country_location', defaults={'place': 'country'}
)
@login_required
def delete_location(place: str):
    place = place.lower()
    if place not in ('country', 'camp'):
        abort(HTTPStatus.NOT_FOUND)

    form = MapLocationForm()
    if form.item_type.data is None or form.item_name.data is None:  # noqa duplicate lines
        flash(_('Invalid form data!'), 'danger')
        return redirect(url_for('main.index'))

    if form.item_type.data not in ('team', 'poi'):
        flash(_('Unknown item type!'), 'danger')
        return redirect(url_for('main.index'))

    item = (
        db.session.query(Team)
        .where(Team.name == form.item_name.data)
        .first()
        if form.item_type.data == 'team'
        else db.session.query(PointOfInterest)
        .where(PointOfInterest.name == form.item_name.data)
        .first()
    )

    if item is None:
        flash(_('Item not found!'), 'danger')
        return redirect(url_for('main.index'))

    if type(item) is Team and current_user.team != item:
        raise PermissionDenied()
    if type(item) is PointOfInterest and not orga_permission.can():
        raise PermissionDenied()

    if place == 'country':
        item.country_location = None
    else:
        item.camp_location = None
    db.session.commit()
    flash(_('Postion deleted!'), 'success')
    if form.item_type.data == 'team':
        return redirect(url_for('settings.team', team_name=form.item_name.data))
    else:
        return redirect(url_for('main.index'))  # TODO adjust
