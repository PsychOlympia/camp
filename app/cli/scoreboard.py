import click

from ..models import db


@click.group('scoreboard', help='Manage the scoreboard data')
def scoreboard():
    pass
