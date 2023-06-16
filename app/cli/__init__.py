from flask import Flask, Blueprint

from .database import database
from .scoreboard import scoreboard
from .teams import teams
from .users import users
from .translate import translate


bp_psy = Blueprint('psy', __name__)
bp_psy.cli.help = 'PyschOlympia related commands'
bp_psy.cli.add_command(database)
bp_psy.cli.add_command(scoreboard)
bp_psy.cli.add_command(teams)
bp_psy.cli.add_command(users)


def cli_init_app(app: Flask) -> None:
    app.register_blueprint(bp_psy)
    app.cli.add_command(translate)
