from __future__ import annotations

from flask import request, current_app
from flask_babel import Babel


def locale_selector() -> str | None:
    return request.accept_languages.best_match(
        current_app.config['BABEL_SUPPORTED_LOCALES'],
        current_app.config['BABEL_DEFAULT_LOCALE']
    )


def timezone_selector() -> str | None:
    """"""
    """
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone
    """
    return None


babel = Babel()
