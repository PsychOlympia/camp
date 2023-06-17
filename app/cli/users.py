from __future__ import annotations

import os
from base64 import b85encode

import click
from click import Context

from ..auth import bcrypt
from ..models import db, User, Team


@click.group('users', help='Manage user logins')
def users():
    pass


@users.command('list', help='List all users')
@click.option(
    '-t', '--teams', 'show_teams',
    is_flag=True, default=False,
    help='Also show the team (if any) for each user'
)
def list_users(show_teams: bool):
    all_users = db.session.query(User).all()
    if len(all_users) <= 0:
        click.echo('There are no users yet!')
        return
    click.echo(f'There are {len(all_users)} users in the database:')
    for user in all_users:
        if show_teams and user.team is not None:
            click.echo(f'- {user.username} ({user.team.name})')
        else:
            click.echo(f'- {user.username}')


@users.command(
    'add',
    short_help='Add a new user to the database',
    help='Add a new user to the database.'
         'If PASSWORD is empty a random password will be generated for this user.'
)
@click.argument('username', required=True)
@click.argument('password', required=False)
@click.option(
    '-t', '--team', 'team_name',
    type=str,
    help='Immediately add this user to a team'
)
@click.option(
    '-c', '--create', '--create-team', 'create_team',
    is_flag=True, default=False,
    help='If used with -t or --team creates a team if a team with that name does not exist'
)
@click.pass_context
def add_user(ctx: Context, username: str, password: str | None, team_name: str | None, create_team: bool):
    if db.session.query(User).where(User.username == username).first() is not None:
        click.secho(f'A user with the username {username} already exists!', fg='bright_red')
        return
    team = db.session.query(Team).where(Team.name == team_name).first()
    if team is None and create_team:
        from .teams import add_team
        ctx.invoke(add_team, team_name=team_name)
        team = db.session.query(Team).where(Team.name == team_name).first()
    if password is None:
        password = b85encode(os.urandom(9)).decode()
        click.secho(f'The random password for {username} is: {password}', fg='bright_blue')
    hashed_password = bcrypt.generate_password_hash(password).decode()
    try:
        if team is None:
            db.session.add(User(username=username, password_hash=hashed_password))  # noqa
            if team_name is not None:
                click.secho(
                    f'The team {team_name} could not be found! The user will not be added to a team.', fg='bright_red'
                )
        else:
            db.session.add(User(username=username, password_hash=hashed_password, team=team))  # noqa
        db.session.commit()
    except Exception as e:
        click.secho(f'Error {e.__class__.__name__}: {e}', fg='bright_red')
        return
    click.secho(f'The user {username} has been added to the database!', fg='bright_green')


@users.command('delete', help='Delete a user')
@click.argument('usernames', nargs=-1, type=str)
@click.option(
    '-y', '--confirm',
    is_flag=True, default=False,
    help='Skip the prompt asking to confirm the delete command'
)
@click.option(
    '-r', '--reset', '--reset-all', 'reset_all',
    is_flag=True, default=False,
    help='Reset the users database'
)
def delete_user(usernames: tuple[str], confirm: bool, reset_all: bool):
    if reset_all and (confirm or click.confirm(click.style(
            'Do you really want to delete every user?', fg='bright_red'
    ))):
        usernames = [user.username for user in db.session.query(User).all()]
        confirm = True

    if len(usernames) <= 0:
        click.secho('There are no users in the database!', fg='bright_red')
        return

    for username in usernames:
        user = db.session.query(User).where(User.username == username).first()
        if user is None:
            click.secho(f'The user {username} does not exist!', fg='bright_red')
            continue
        if not confirm and not click.confirm(click.style(
                f'Do you really want to delete the user {username}?', fg='bright_yellow'
        )):
            continue
        db.session.delete(user)
        db.session.commit()
        click.secho(f'The user {username} has been deleted!', fg='bright_green')
