import click
from click import Context
from sqlalchemy.exc import IntegrityError

from ..models import db, Team


@click.group('teams', help='Manage teams')
def teams():
    pass


@teams.command('list', help='Show all teams that are currently in the database')
@click.option(
    '-m', '--members', 'show_members',
    is_flag=True,
    default=False,
    help='Also show the members (if any) of this team'
)
def list_teams(show_members: bool):
    all_teams = db.session.query(Team).all()
    if len(all_teams) <= 0:
        click.echo('There are no teams yet!')
        return
    click.echo(f'There are {len(all_teams)} teams in the database:')
    for team in all_teams:
        if show_members and len(team.members) > 0:
            click.echo(f'- {team.name} ({", ".join(member.username for member in team.members)})')
        else:
            click.echo(f'- {team.name}')


@teams.command('add', help='Add a team to the database')
@click.argument('team_name')
def add_team(team_name: str):
    try:
        db.session.add(Team(name=team_name))
        db.session.commit()
        click.secho(f'Team {team_name} was successfully added to the database!', fg='bright_green')
    except IntegrityError:
        click.secho(f'A team with the name {team_name} already exists!"', fg='bright_red')
    except Exception as e:
        click.secho(f'Error {e.__class__.__name__}: {e}', fg='bright_red')


@teams.command('delete', help='Delete a team')
@click.argument('team_names', nargs=-1, type=str)
@click.option(
    '-y', '--confirm',
    is_flag=True, default=False,
    help='Skip the prompt asking to confirm the delete command'
)
@click.option(
    '-r', '--reset', '--reset-all', 'reset_all',
    is_flag=True, default=False,
    help='Reset the teams database'
)
@click.option(
    '-m', '--members', '--delete-members', 'delete_members',
    is_flag=True, default=False,
    help='Also delete every user that is a member of this team'
)
@click.pass_context
def delete_team(ctx: Context, team_names: tuple[str], confirm: bool, reset_all: bool, delete_members: bool):
    if reset_all and (confirm or click.confirm(click.style(
            'Do you really want to delete every team?', fg='bright_red'
    ))):
        team_names = [team.name for team in db.session.query(Team).all()]
        confirm = True

    if len(team_names) <= 0:
        click.secho('There are no teams in the database!', fg='bright_red')
        return

    for team_name in team_names:
        team = db.session.query(Team).where(Team.name == team_name).first()
        if team is None:
            click.secho(f'The team {team_name} does not exist!', fg='bright_red')
            continue
        if not confirm:
            if delete_members:
                if not click.confirm(click.style(
                    f'Do you really want to delete the team {team_name} and all of its members?', fg='bright_yellow'
                )):
                    continue
            elif click.confirm(click.style(
                f'Do you really want to delete the team {team_name}?', fg='bright_yellow'
            )):
                continue
        if delete_members and len(team.members) > 0:
            from .users import delete_user
            ctx.invoke(delete_user, usernames=[member.username for member in team.members], confirm=True)
        db.session.delete(team)
        db.session.commit()
        click.secho(f'The team {team_name} has been deleted!', fg='bright_green')
