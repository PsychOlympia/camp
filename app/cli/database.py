import click

from ..models import db


@click.group('database', help='Manage the database')
def database():
    pass


@database.command('reset', help='Reset everything')
@click.option(
    '-y', '--confirm', 'confirm',
    is_flag=True, default=False,
    help='Skip the prompt asking to confirm the command'
)
def reset(confirm: bool):
    if not confirm:
        click.confirm(click.style('Do you really want to reset the whole database?', fg='bright_red'), abort=True)
    try:
        db.drop_all()
        click.secho('The database has been reset!', fg='bright_green')
    except Exception as e:
        click.secho(f'Error {e.__class__.__name__}: {e}', fg='bright_red')
