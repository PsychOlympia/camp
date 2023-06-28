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
            existing_feedback = WebsiteFeedback(user=current_user)  # TODO save feedback
            db.session.add(existing_feedback)
            db.session.commit()
        return redirect(url_for('.website'))

    form.user.data = current_user.id
    if existing_feedback is not None:
        feedback_exists = True

    return render_template(
        'feedback_website.jinja2',
        website_feedback_form=form,
        feedback_exists=feedback_exists
    )


@bp_feedback.route('/wifi', methods=['GET', 'POST'], endpoint='wifi')
@login_required
def wifi():
    feedback_exists = False
    wifi_feedback_form = WiFiFeedbackForm()
    existing_feedback = db.session.query(WiFiFeedback).where(WiFiFeedback.user == current_user).first()

    if request.method == 'POST':
        flash(_('Thank you for your feedback!'), 'success')
        if existing_feedback is None:
            existing_feedback = WiFiFeedback(user=current_user)  # TODO save feedback
            db.session.add(existing_feedback)
            db.session.commit()
        return redirect(url_for('.wifi'))

    wifi_feedback_form.user.data = current_user.id
    if existing_feedback is not None:
        feedback_exists = True

    return render_template(
        'feedback_wifi.jinja2',
        wifi_feedback_form=wifi_feedback_form,
        feedback_exists=feedback_exists
    )
