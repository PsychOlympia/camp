import click

from ..models import db


@click.group('database', help='Manage the database')
def database():
    pass


@database.command('reset', help='Reset everything')
def reset():
    try:
        db.drop_all()
        click.echo('The database has been reset!')
    except Exception as e:
        click.echo(f'Error {e.__class__.__name__}: {e}')
