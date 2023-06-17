import click
from sqlalchemy.exc import IntegrityError

from ..models import db, Team


@click.group('teams', help='Manage teams')
def teams():
    pass


@teams.command('show', help='Show all teams that are currently in the database')
def show_teams():
    teams_ = db.session.query(Team).all()
    if len(teams_) <= 0:
        click.echo('There are no teams in the database yet!')
        return
    click.echo('Teams in the database:')
    for team in teams_:
        click.echo(f'- {team.name}')


@teams.command('add', help='Add a team to the database')
@click.argument('team_name')
def add_team(team_name: str):
    try:
        db.session.add(Team(name=team_name))
        db.session.commit()
        click.echo(f'Team "{team_name}" was successfully added to the database!')
    except IntegrityError:
        click.echo(f'A team with the name "{team_name}" already exists!"')
    except Exception as e:
        click.echo(f'Error {e.__class__.__name__}: {e}')
