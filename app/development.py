from functools import wraps

from flask import flash
from flask_babel import gettext as _


def experimental(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        flash(_('EXPERIMENTAL SITE!'), 'danger')
        return func(*args, **kwargs)

    return wrapper
