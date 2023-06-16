import click

from ..models import db


@click.group('users', help='Manage user logins')
def users():
    pass
