import csv

import click
from click import Context
from sqlalchemy.exc import IntegrityError

from ..models import db, Team, deserialize_coordinates, User, serialize_coordinates


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
        click.secho(f'The team {team_name} was successfully added to the database!', fg='bright_green')
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


@teams.command(
    'import',
    short_help='Import teams from a CSV file',
    help='Import teams from a CSV file. The CSV_FILE is the file to import teams from, '
         'or in case of --template the template file path'
)
@click.argument('csv_file')
@click.option(
    '-t', '--template', 'template',
    is_flag=True, default=False,
    help='Do not import teams, but rather export a template CSV to fill with data'
)
def import_teams(csv_file: str, template: bool):
    if not csv_file.lower().endswith('.csv'):
        csv_file = f'{csv_file}.csv'
    if template:
        click.secho(f'Writing template to to {csv_file}', fg='bright_blue')
        with open(csv_file, mode='w') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([
                ('Teamname', 'Team accent-color', 'Team category', 'Camp location', 'Country location', 'Team member 1 name', 'Team member 2 name', '...'),
                ('Testteam', '#0000ff', 'team', '51.165,10.455278', None, 'user1', 'user2', 'user3', 'user4')
            ])
        return
    with open(csv_file, mode='r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for line in reader:
            if len(line) == 0:
                continue
            if len(line) < 5:
                click.secho(f'Skipping line {reader.line_num}: Not enough values!')
                continue
            name, accent_color, category, camp_coordinates, country_coordinates, *member_names = line
            if db.session.query(Team).where(Team.name == name.strip()).first() is not None:
                click.secho(f'The team {name} already exists!', fg='bright_yellow')
                continue
            camp_coordinates = deserialize_coordinates(camp_coordinates)
            country_coordinates = deserialize_coordinates(country_coordinates)
            team = Team(
                name=name.strip(),
                _camp_location=serialize_coordinates(camp_coordinates),
                _country_location=serialize_coordinates(country_coordinates),
                color=None if accent_color.strip() == '' else accent_color.strip(),
                category=None if category.strip() == '' else category.strip(),
                members=db.session.query(User).where(User.username.in_(member_names)).all()
            )
            db.session.add(team)
            db.session.commit()
