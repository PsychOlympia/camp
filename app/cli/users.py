from __future__ import annotations

import os
from base64 import b85encode

import click
from click import Context

from ..auth import bcrypt, RoleName
from ..models import db, User, Team, Role


@click.group('users', help='Manage users')
def users():
    pass


@users.command('list', help='List all users')
@click.option(
    '-t', '--teams', 'show_teams',
    is_flag=True, default=False,
    help='Also show the team (if any) for each user'
)
@click.option(
    '-r', '--roles', 'show_roles',
    is_flag=True, default=False,
    help='Also show the roles (if any) for each user'
)
def list_users(show_teams: bool, show_roles: bool):
    all_users = db.session.query(User).all()
    if len(all_users) <= 0:
        click.echo('There are no users yet!')
        return
    click.echo(f'There are {len(all_users)} users in the database:')
    for user in all_users:
        line = f'- {user.username}'
        if show_roles and len(user.roles) > 0:
            line = f'{line}:{",".join(map(lambda role: role.name, user.roles))}'
        if show_teams and user.team is not None:
            line = f'{line} ({user.team.name})'
        click.echo(line)


@users.command(
    'add',
    short_help='Add a new user to the database',
    help='Add a new user to the database. '
         'If PASSWORD is empty a random password will be generated for this user. '
         'To add multiple roles for the user repeatedly supply -r or --role followed by the role name.'
)
@click.argument('username', type=str, required=True)
@click.argument('password', type=str, required=False)
@click.option(
    '-t', '--team', 'team_name',
    type=str,
    help='Immediately add this user to a team.'
)
@click.option(
    '-r', '--role', 'user_roles',
    type=str, multiple=True,
    help='Immediately add a role to this user.'
)
@click.option(
    '-c', '--create', '--create-team', 'create_team',
    is_flag=True, default=False,
    help='If used with -t or --team creates a team if a team with that name does not exist instead of failing.'
)
@click.pass_context
def add_user(
        ctx: Context,
        username: str,
        password: str | None,
        team_name: str | None,
        create_team: bool,
        user_roles: tuple[str]
):
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
        user = User(username=username, password_hash=hashed_password)  # noqa
        if team is None and team_name is not None:
            click.secho(
                f'The team {team_name} could not be found! The user will not be added to a team.', fg='bright_yellow'
            )
        elif team is not None:
            user.team = team
        db.session.add(user)
        db.session.commit()
        click.secho(f'The user {username} has been added to the database!', fg='bright_green')
        if len(user_roles) > 0:
            ctx.invoke(add_role, username=username, user_roles=user_roles)
    except Exception as e:
        click.secho(f'Error {e.__class__.__name__}: {e}', fg='bright_red')
        return


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


@users.group('role', help='Manage roles for a user')
def roles():
    pass


@roles.command('add', help='Add a role to a user. To add multiple roles at once just pass them as additional arguments')
@click.argument('username', type=str, required=True)
@click.argument('user_roles', type=str, nargs=-1, required=True)
def add_role(username: str, user_roles: tuple[str]):
    user = db.session.query(User).where(User.username == username).first()
    if user is None:
        click.secho(f'A user with the username {username} does not exist!', fg='bright_red')
        return
    for role_name in user_roles:
        if role_name not in map(lambda m: m.value, RoleName.__members__.values()):
            click.secho(
                f'The role {role_name} does not exist and therefore will not be added to {username}!', fg='bright_red'
            )
            continue
        if role_name in map(lambda role: role.name, user.roles):
            click.secho(f'The user {username} already has the role {role_name}!', fg='bright_yellow')
            continue
        user.roles.append(Role(name=role_name))
        db.session.commit()
        click.secho(f'The role {role_name} has been added to the user {username}.', fg='bright_green')


@roles.command(
    'remove',
    help='Remove a role to a user. To remove multiple roles at once just pass them as additional arguments'
)
@click.argument('username', type=str, required=True)
@click.argument('user_roles', type=str, nargs=-1, required=True)
def remove_role(username: str, user_roles: tuple[str]):
    user = db.session.query(User).where(User.username == username).first()
    if user is None:
        click.secho(f'A user with the username {username} does not exist!', fg='bright_red')
        return
    for role_name in user_roles:
        if role_name not in map(lambda role: role.name, user.roles):
            click.secho(f'The user {username} does not have the role {role_name}!', fg='bright_yellow')
            continue
        user.roles.remove(list(filter(lambda role: role.name == role_name, user.roles))[0])
        db.session.commit()
        click.secho(f'The role {role_name} has been removed form the user {username}.', fg='bright_green')


@roles.command('list', help='List the available roles')
def list_roles():
    click.echo('Available roles:')
    click.echo(', '.join(map(lambda m: m.value, RoleName.__members__.values())))
