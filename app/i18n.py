from __future__ import annotations

from flask import request, current_app
from flask_babel import Babel
from flask_login import current_user


def locale_selector() -> str | None:
    if current_user.is_authenticated:
        if current_user.locale in current_app.config['BABEL_SUPPORTED_LOCALES']:
            return current_user.locale

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
