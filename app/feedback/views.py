from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required

from .forms import WiFiFeedbackForm, WebsiteFeedbackForm
from ..models import db, WebsiteFeedback, WiFiFeedback

bp_feedback = Blueprint(
    'feedback', __name__, template_folder='templates', static_folder='static', url_prefix='/feedback'
)


@bp_feedback.route('/website', methods=['GET', 'POST'], endpoint='website')
@login_required
def website():
    feedback_exists = False
    form = WebsiteFeedbackForm()
    existing_feedback = db.session.query(WebsiteFeedback).where(WebsiteFeedback.user == current_user).first()

    if request.method == 'POST':
        flash(_('Thank you for your feedback!'), 'success')
        if existing_feedback is None:
            existing_feedback = WebsiteFeedback(
                user=current_user,
                keep=form.keep.data,
                remove=form.remove.data,
                add=form.add.data,
                further_notes=form.further_notes.data
            )
            db.session.add(existing_feedback)
        else:
            existing_feedback.keep = form.keep.data
            existing_feedback.remove = form.remove.data
            existing_feedback.add = form.add.data
            existing_feedback.further_notes = form.further_notes.data
        db.session.commit()
        return redirect(url_for('.website'))

    form.user.data = current_user.id
    if existing_feedback is not None:
        feedback_exists = True
        form.keep.data = existing_feedback.keep
        form.remove.data = existing_feedback.remove
        form.add.data = existing_feedback.add
        form.further_notes.data = existing_feedback.further_notes

    return render_template(
        'feedback_website.jinja2',
        website_feedback_form=form,
        feedback_exists=feedback_exists
    )


@bp_feedback.route('/website/revoke', methods=['POST'], endpoint='website_revoke')
@login_required
def revoke_website():
    existing_feedback = db.session.query(WebsiteFeedback).where(WebsiteFeedback.user == current_user).first()
    if existing_feedback is None:
        flash(_('You have not submitted a feedback yet!'), 'danger')
        return redirect(url_for('.website'))

    db.session.delete(existing_feedback)
    db.session.commit()
    flash(_('Your feedback has been deleted!'), 'success')
    return redirect(url_for('.website'))


@bp_feedback.route('/wifi', methods=['GET', 'POST'], endpoint='wifi')
@login_required
def wifi():
    feedback_exists = False
    wifi_feedback_form = WiFiFeedbackForm()
    existing_feedback = db.session.query(WiFiFeedback).where(WiFiFeedback.user == current_user).first()

    if request.method == 'POST':
        flash(_('Thank you for your feedback!'), 'success')
        if existing_feedback is None:
            existing_feedback = WiFiFeedback(
                user=current_user,
                quality=wifi_feedback_form.quality.data,
                further_notes=wifi_feedback_form.further_notes.data
            )
            existing_feedback.coverage = wifi_feedback_form.coverage.data
            db.session.add(existing_feedback)
        else:
            existing_feedback.quality = wifi_feedback_form.quality.data
            existing_feedback.further_notes = wifi_feedback_form.further_notes.data
            existing_feedback.coverage = wifi_feedback_form.coverage.data
        db.session.commit()
        return redirect(url_for('.wifi'))

    wifi_feedback_form.user.data = current_user.id
    if existing_feedback is not None:
        wifi_feedback_form.quality.data = existing_feedback.quality
        wifi_feedback_form.further_notes.data = existing_feedback.further_notes
        wifi_feedback_form.coverage.data = existing_feedback.coverage
        feedback_exists = True

    return render_template(
        'feedback_wifi.jinja2',
        wifi_feedback_form=wifi_feedback_form,
        feedback_exists=feedback_exists
    )


@bp_feedback.route('/wifi/revoke', methods=['POST'], endpoint='wifi_revoke')
@login_required
def revoke_wifi():
    existing_feedback = db.session.query(WiFiFeedback).where(WiFiFeedback.user == current_user).first()
    if existing_feedback is None:
        flash(_('You have not submitted a feedback yet!'), 'danger')
        return redirect(url_for('.wifi'))

    db.session.delete(existing_feedback)
    db.session.commit()
    flash(_('Your feedback has been deleted!'), 'success')
    return redirect(url_for('.wifi'))
