from http import HTTPStatus

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required
from sqlalchemy import desc, func

from .forms import AddPointsForm
from ..auth import team_permission
from ..models import db, Scoreboard, ScoreboardEntry, Team

bp_scoreboard = Blueprint(
    'scoreboard', __name__, template_folder='templates', static_folder='static', url_prefix='/scoreboard'
)


@bp_scoreboard.route('/', methods=['GET'], endpoint='index')
@login_required
@team_permission.require(http_exception=HTTPStatus.UNAUTHORIZED)
def index():
    latest_scoreboard = db.session.query(Scoreboard).order_by(desc(Scoreboard.round)).first()
    add_points_form = AddPointsForm()
    add_points_form.team.choices = [(team.id, team.name) for team in db.session.query(Team).all()]
    if latest_scoreboard is not None:
        add_points_form.round.data = latest_scoreboard.round
    add_points_form.points.data = 1

    round_number = request.args.get('round')
    if (round_number is None
            or not round_number.isdecimal()
            or db.session.query(Scoreboard).where(Scoreboard.round == int(round_number)).first() is None):
        scoreboard = db.session.query(Scoreboard).where(
            func.length(Scoreboard.entries) > 0
        ).order_by(desc(Scoreboard.round)).first()
    else:
        scoreboard = db.session.query(Scoreboard).where(Scoreboard.round == int(round_number)).first()
    if scoreboard is None:
        flash('Scoreboard not available!')  # TODO handle
    return render_template('scoreboard.jinja2', scoreboard=scoreboard, latest_scoreboard=latest_scoreboard,
        add_points_form=add_points_form)


@bp_scoreboard.route('/new', methods=['POST'], endpoint='new')
def new():
    scoreboard = Scoreboard()
    db.session.add(scoreboard)
    db.session.commit()
    flash(f'New scoreboard (round {scoreboard.round})')
    return redirect(url_for('helper.index'))


@bp_scoreboard.route('/fill')
def fill():
    for team_name in ('Team 1', 'Team 2', 'Team 3', 'Team 4', 'Team 5', 'Team 6', 'Team 7', 'Team 8', 'Team 9'):
        db.session.add(Team(name=team_name))
    db.session.commit()
    return redirect(url_for('.index'))


@bp_scoreboard.route('/add-points', methods=['POST'], endpoint='add_points')
def add_points():
    add_points_form = AddPointsForm()
    scoreboard = db.session.query(Scoreboard).where(Scoreboard.round == add_points_form.round.data).first()
    if scoreboard is None:
        flash('Scoreboard not found!')
    flash(f'Selected scoreboard with round {scoreboard.round}')

    team = db.session.query(Team).where(Team.id == add_points_form.team.data).first()
    if team is None:
        flash('Team is None')
    flash(f'Selected team {team.name}')

    entry = db.session.query(ScoreboardEntry).where(
        ScoreboardEntry.team == team and ScoreboardEntry.round == add_points_form.round.data
    ).first()
    flash(f'{entry}')
    if entry is None:
        flash('Entry was None')
        entry = ScoreboardEntry(team=team, scoreboard=scoreboard, round=scoreboard.round)
        db.session.add(entry)
        db.session.commit()
    else:
        flash('Entry exists')
    entry.score += add_points_form.points.data
    db.session.commit()
    flash(f'Added {add_points_form.points.data} -> {entry.score} (round {entry.round})')
    return redirect(url_for('helper.index'))
