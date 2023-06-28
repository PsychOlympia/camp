import click
from click import Context
from flask import current_app
from sqlalchemy.exc import IntegrityError

from ..auth import RoleName
from ..models import db, PointOfInterest, serialize_coordinates


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


@database.command('init', help='Create the minimal needed objects')
@click.pass_context
def init(ctx: Context):
    from .users import add_user
    ctx.invoke(add_user, username='root', user_roles=tuple(member.value for member in RoleName.__members__.values()))
    camp_location = serialize_coordinates((
        float(current_app.config['CAMP_LOCATION_LAT']), float(current_app.config['CAMP_LOCATION_LON'])
    ))
    db.session.add(PointOfInterest(
        name='PsychOlympia',
        _camp_location=None,
        _country_location=camp_location,
        linkable=False
    ))
    try:
        db.session.commit()
        click.secho("Added POI 'PsychOlympia' to the database.", fg='bright_green')
    except IntegrityError:
        click.secho("The database already contains the POI 'PsychOlympia'", fg='bright_red')
        db.session.rollback()

    db.session.add(PointOfInterest(
        name='Infostand',
        _camp_location=serialize_coordinates((
            float(current_app.config['INFO_LOCATION_LAT']), float(current_app.config['INFO_LOCATION_LON'])
        )),
        _country_location=None,
        linkable=False
    ))
    try:
        db.session.commit()
        click.secho("Added POI 'Infostand' to the database.", fg='bright_green')
    except IntegrityError:
        click.secho("The database already contains the POI 'Infostand'", fg='bright_red')
        db.session.rollback()
    click.secho('Initialized database', fg='bright_green')
