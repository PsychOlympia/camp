import os
import sys
import zipfile
import urllib.request
from pathlib import Path

import click
from flask import current_app


@click.group('maps', help='Manage downloaded maps')
def maps():
    pass


@maps.command(
    'init',
    short_help='Install requirements',
    help='Install requirements. Currently only windows is supported'
)
def init():
    def report(block_number, block_size, total):
        percent = block_number * block_size / total * 100
        click.secho(
            f'\rProgress: {percent:.0f}%',
            nl=percent >= 100,
            fg='bright_green' if percent >= 100 else 'bright_yellow'
        )

    zip_file = Path('Maperitive-latest.zip')
    click.secho('Downloading Maperitive ...', fg='bright_blue')
    try:
        if sys.platform not in ('win32', 'cgywin'):
            os.system('apt install libmono-winforms2.0-cil mono-devel')
        urllib.request.urlretrieve(
            'http://maperitive.net/download/Maperitive-latest.zip',
            zip_file,
            reporthook=report
        )
        click.secho('Extracting ...', fg='bright_blue')
        with zipfile.ZipFile(zip_file) as zip_ref:
            zip_ref.extractall('.')
        zip_file.unlink(missing_ok=True)
    except Exception as e:
        click.secho(f'Error {e.__class__.__name__}: {e}', fg='bright_red')
        return
    click.secho('Done', fg='bright_green')


@maps.command(
    'download',
    short_help='EXPERIMENTAL: Download maps for offline use',
    help='EXPERIMENTAL: Download maps for offline use. This command should not be used!'
)
@click.option(
    '--camp', '--camp-only', 'camp_only',
    is_flag=True, default=False,
    help='Only download the map for the camp'
)
@click.option(
    '--country', '--country-only', 'country_only',
    is_flag=True, default=False,
    help='Only download the map for the country'
)
@click.option(
    '-e', '--eco', 'eco',
    is_flag=True, default=False,
    help='Download just the relevant portions of the map. Helpful when using bounds restrictions on maps to save space.'
)
def download(camp_only: bool, country_only: bool, eco: bool):
    if all((camp_only, country_only)):
        click.secho('Use at most one flag for download!', fg='bright_red')
        return

    cwd = os.getcwd()
    maperitive_dir = Path('Maperitive').absolute()
    output_path = (Path('app') / 'static' / 'maps').absolute()
    script = Path('script.mscript').absolute()

    if sys.platform in ('win32', 'cgywin'):
        os.chdir(maperitive_dir)
        executable = 'Maperitive.Console.exe'
    else:
        executable = f'mono "{maperitive_dir / "Maperitive.Console.exe"}"'

    try:
        prefixes = ['camp', 'country']
        if camp_only:
            prefixes = ['camp']
        if country_only:
            prefixes = ['country']

        for prefix in prefixes:
            tiles_dir = output_path / prefix.lower()
            tiles_dir.mkdir(exist_ok=True)
            if len(os.listdir(tiles_dir)) > 0 and not click.confirm(click.style(
                    f'{prefix} seems to be already downloaded. Do you want to download {prefix} again?',
                    fg='bright_yellow'
            )):
                continue
            x = float(current_app.config[f'{prefix.upper()}_LOCATION_LON'])
            y = float(current_app.config[f'{prefix.upper()}_LOCATION_LAT'])
            zoom = int(current_app.config[f'{prefix.upper()}_LOCATION_ZOOM'])
            min_zoom = int(current_app.config[f'{prefix.upper()}_LOCATION_MIN_ZOOM'])
            max_zoom = int(current_app.config[f'{prefix.upper()}_LOCATION_MAX_ZOOM'])
            if eco:
                commands = [
                    'use-ruleset alias=default',
                    'add-web-map',
                ]
                for zoom_level in range(min_zoom, max_zoom + 1):
                    commands.extend([
                        f'move-pos x={x} y={y} zoom={zoom_level}',
                        f'set-geo-bounds '
                        f'{x - 2 ** (10 - zoom_level)},{y - 2 ** (10 - zoom_level) * 0.5},'
                        f'{x + 2 ** (10 - zoom_level)},{y + 2 ** (10 - zoom_level) * 0.5}',
                        f'generate-tiles minzoom={zoom_level} maxzoom={zoom_level} tilesdir="{tiles_dir}"'
                    ])
            else:
                commands = [
                    'use-ruleset alias=default',
                    'add-web-map',
                    f'move-pos x={x} y={y} zoom={zoom}',
                    f'set-geo-bounds '
                    f'{x-2**(10-min_zoom)},{y-2**(10-min_zoom)*0.5},'  # TODO find good function for y instead of x*0.5
                    f'{x+2**(10-min_zoom)},{y+2**(10-min_zoom)*0.5}',  # TODO find good function for y instead of x*0.5
                    f'generate-tiles minzoom={min_zoom} maxzoom={max_zoom} tilesdir="{tiles_dir}"'
                ]
            with open(script, mode='w') as f:
                f.writelines(f'{line}\n' for line in commands)
            click.secho('Executing Maperitive, this may take a while!', fg='bright_yellow')
            # print(commands)
            os.system(f'{executable} {script}')
            script.unlink(missing_ok=True)
            (tiles_dir / 'tiles.json').unlink(missing_ok=True)
            click.secho(f'Completed download of {prefix}!', fg='bright_green')
    finally:
        if sys.platform in ('win32', 'cgywin'):
            os.chdir(cwd)
    click.secho('Completed all downloads', fg='bright_green')
