from __future__ import annotations

import os
from base64 import b85encode

import click

from ..auth import bcrypt
from ..models import db, User


@click.group('users', help='Manage user logins')
def users():
    pass


@users.command(
    'add',
    short_help='Add a new user to the database',
    help='Add a new user to the database.'
         'If PASSWORD is empty a random password will be generated for this user.'
)
@click.argument('username', required=True)
@click.argument('password', required=False)
def add_user(username: str, password: str | None):
    if db.session.query(User).where(User.username == username).first() is not None:
        click.echo(f'A user with the username {username} already exists!')
        return
    if password is None:
        password = b85encode(os.urandom(9)).decode()
        click.echo(f'The random password for {username} is: {password}')
    hashed_password = bcrypt.generate_password_hash(password).decode()
    try:
        db.session.add(User(username=username, password_hash=hashed_password))  # noqa
        db.session.commit()
    except Exception as e:
        click.echo(f'Error {e.__class__.__name__}: {e}')
        return
    click.echo(f'The user {username} has been added to the database!')


@users.command('delete', help='Delete a user')
@click.argument('username')
@click.option(
    '-y', '--confirm',
    is_flag=True,
    default=False,
    help='Skip the prompt asking to confirm the delete command'
)
def delete_user(username: str, confirm: bool):
    user = db.session.query(User).where(User.username == username).first()
    if user is None:
        click.echo(f'The user {username} does not exist!')
        return
    if not confirm and not click.confirm(f'Do you really want to delete the user {username}?'):
        return
    db.session.delete(user)
    db.session.commit()
    click.echo(f'The user {username} has been deleted!')
