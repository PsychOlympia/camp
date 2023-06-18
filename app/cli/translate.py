from __future__ import annotations

import os
import click

from flask import current_app
from babel import Locale, UnknownLocaleError
from pathlib import Path


@click.group('translate', help='Manage translations')
def translate():
    pass


@translate.command(name='update', help='Update all languages.')
def update_command():
    _config_directory = current_app.config.get('BABEL_TRANSLATION_DIRECTORIES', 'translations').split(';')[0]  # noqa
    translations_directory = Path(current_app.root_path) / _config_directory
    domain = current_app.config.get('BABEL_DOMAIN', 'messages').split(';')[0]

    config_file = Path(current_app.config['BABEL_CONFIG_FILE'])
    if not config_file.exists():
        raise RuntimeError(f'File {config_file} does not exist')
    if os.system(f'pybabel extract -F {config_file} -k _l -o "{translations_directory}/{domain}.pot" .'):
        raise RuntimeError('extract command failed')
    if os.system(f'pybabel update -i "{translations_directory}/{domain}.pot" -d "{translations_directory}"'):
        raise RuntimeError('update command failed')
    (Path(translations_directory) / f'{domain}.pot').unlink(missing_ok=True)


@translate.command(name='compile', help='Compile all languages.')
def compile_command():
    _config_directory = current_app.config.get('BABEL_TRANSLATION_DIRECTORIES', 'translations').split(';')[0]
    translations_directory = Path(current_app.root_path) / _config_directory

    if os.system(f'pybabel compile -d "{translations_directory}"'):
        raise RuntimeError('compile command failed')


@translate.command(name='init', help='Initialize a new language.')
@click.argument('lang')
def init_command(lang):
    _config_directory = current_app.config.get('BABEL_TRANSLATION_DIRECTORIES', 'translations').split(';')[0]  # noqa
    translations_directory = Path(current_app.root_path) / _config_directory
    domain = current_app.config.get('BABEL_DOMAIN', 'messages').split(';')[0]

    config_file = Path(current_app.config['BABEL_CONFIG_FILE'])
    if not config_file.exists():
        raise RuntimeError(f'File {config_file} does not exist')
    try:
        Locale.parse(lang)
    except UnknownLocaleError:
        click.echo(f'Unknown locale: {lang}')
        return
    if (Path(domain) / lang / 'LC_MESSAGES').exists():
        click.confirm(
            text=f'A folder for the language {lang} already exists. Are you sure you want to initialize {lang}?',
            abort=True
        )
    if os.system(f'pybabel extract -F {config_file} -k _l -o "{translations_directory}/{domain}.pot" .'):
        raise RuntimeError('extract command failed')
    if os.system(f'pybabel init -i "{translations_directory}/{domain}.pot" -d "{translations_directory}" -l "{lang}"'):
        raise RuntimeError('init command failed')
    (Path(translations_directory) / f'{domain}.pot').unlink(missing_ok=True)
