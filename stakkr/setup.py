# coding: utf-8
"""Setup post actions, used in main setup.py."""

import os
import shutil
import sys
import click
from yaml import load, dump
from stakkr import file_utils
from stakkr.actions import StakkrActions


@click.command(help="""Initialize for the first time stakkr by copying
templates and directory structure""")
@click.option('--force', '-f', help="Force recreate directories structure", is_flag=True)
@click.argument('recipe', required=False)
def init(force: bool, recipe: str = None):
    """CLI Entry point, when initializing stakkr manually."""
    config_file = os.getcwd() + '/stakkr.yml'
    if os.path.isfile(config_file) and force is False:
        click.secho('Config file (stakkr.yml) already present. Leaving.', fg='yellow')
        return

    click.secho('Create some required files / directories', fg='green')
    install_filetree(force)
    if recipe is not None:
        install_recipe(recipe.lower())
        msg = "Recipe has been installed"
    else:
        msg = "Config (stakkr.yml) not present, don't forget to create it"

    click.secho(msg, fg='green')


def install_filetree(force: bool = False):
    """Create templates (directories and files)."""
    required_dirs = [
        'conf/mysql-override',
        'conf/php-fpm-override',
        'conf/xhgui-override',
        'data',
        'home/www-data',
        'home/www-data/bin',
        'logs',
        'services',
        'www'
    ]
    for required_dir in required_dirs:
        _create_dir(os.getcwd(), required_dir, force)

    required_tpls = [
        # 'bash_completion', # How to do with a system wide installation ?
        'stakkr.yml.tpl',
        'conf/mysql-override/mysqld.cnf',
        'conf/php-fpm-override/example.conf',
        'conf/php-fpm-override/README',
        'conf/xhgui-override/config.php',
        'home/www-data/.bashrc'
    ]
    for required_tpl in required_tpls:
        _copy_file(os.getcwd(), required_tpl, force)


def install_recipe(recipe: str):
    """Install a recipe (do all tasks)"""
    # Get config
    recipe_config = _recipe_get_config(recipe)
    with open(recipe_config, 'r') as stream:
        recipe = load(stream)

    # Install everything declared in the recipe
    click.secho('Installing services')
    _recipe_install_services(recipe['services'])

    click.secho('Creating config')
    _recipe_create_stakkr_config(recipe['config'])

    click.secho('Starting stakkr (can take a few minutes)')
    stakkr = _recipe_init_stakkr()
    stakkr.start(None, True, True, True)

    click.secho('Running commands')
    _recipe_run_commands(stakkr, recipe['commands'])
    _recipe_display_messages(stakkr, recipe['messages'])


def _create_dir(project_dir: str, dir_name: str, force: bool):
    """Create a directory from stakkr skel"""
    dir_name = project_dir + '/' + dir_name.lstrip('/')
    if os.path.isdir(dir_name) and force is False:
        return

    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)


def _copy_file(project_dir: str, source_file: str, force: bool):
    """Copy a file from a template to project dir"""
    full_path = file_utils.get_file('tpls', source_file)
    dest_file = project_dir + '/' + source_file
    if os.path.isfile(dest_file) and force is False:
        click.secho('  - {} exists, do not overwrite'.format(source_file))
        return

    click.secho('  - {} written'.format(source_file))
    try:
        shutil.copy(full_path, dest_file)
    except Exception:
        msg = "Error trying to copy {} .. check that the file is there ...".format(full_path)
        print(msg, file=sys.stderr)


def _recipe_get_config(recipe: str):
    """Get recipe"""
    if recipe is None:
        return ''

    recipe_config = file_utils.get_file('static/recipes', '{}.yml'.format(recipe))
    if os.path.isfile(recipe_config) is False:
        click.secho('"{}" recipe does not exist'.format(recipe), fg='red')
        sys.exit(1)

    return recipe_config


def _recipe_create_stakkr_config(config: dict):
    """Build stakkr config from recipe"""
    with open('stakkr.yml', 'w') as outfile:
        dump(config, outfile, default_flow_style=False)


def _recipe_install_services(services: list):
    """Install services defined in recipe"""
    from stakkr.services import install

    for service in services:
        success, message = install('services', service, service)
        if success is False:
            click.echo(click.style('    😧 {}'.format(message), fg='red'))
            sys.exit(1)

        if message is not None:
            click.echo(click.style('    😊 {}'.format(message), fg='yellow'))
            continue

        click.echo(click.style('    😀 Package "{}" Installed'.format(service), fg='green'))


def _recipe_init_stakkr():
    """Initialize Stakkr"""
    return StakkrActions({
        'CONFIG': '{}/stakkr.yml'.format(os.getcwd()),
        'VERBOSE': False,
        'DEBUG': False
    })


def _recipe_run_commands(stakkr: StakkrActions, commands: str):
    """Run all commands defined in recipe"""
    for title, cmd in commands.items():
        click.secho('  ↳ {}'.format(title))
        user = cmd['user'] if 'user' in cmd else 'root'
        stakkr.exec_cmd(cmd['container'], user, cmd['args'], True)


def _recipe_display_messages(stakkr: StakkrActions, recipe_messages: list):
    """Build messages to display after installing a recipe"""
    services_ports = stakkr.get_services_urls()
    click.secho('\nServices URLs :')
    click.secho(services_ports)

    if recipe_messages:
        click.secho('Recipe messages:', fg='green')

    for message in recipe_messages:
        click.secho('  - {}'.format(message))
