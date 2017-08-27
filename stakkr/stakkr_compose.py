"""
CLI Tool that wrap docker-compose and build it from what has been taken from config
"""

import os
import subprocess
import sys
import click
from stakkr import package_utils
from stakkr.configreader import Config


@click.command(help="Wrapper for docker-compose",
               context_settings=dict(ignore_unknown_options=True))
@click.option('--config', '-c', help="Override the conf/compose.ini")
@click.argument('command', nargs=-1, type=click.UNPROCESSED)
def cli(config: str, command):
    """Command line entry point"""

    main_config = get_main_config(config)
    set_env_values_from_conf(main_config)

    project_name = main_config.get('project_name')
    os.putenv('COMPOSE_PROJECT_NAME', project_name)

    # What to load
    compose_file = package_utils.get_file('static', 'docker-compose.yml')
    activated_services = get_enabled_services(main_config.get('services'))

    # Create the command
    services = []
    for service in activated_services:
        services.append('-f')
        services.append(service)

    base_cmd = ['docker-compose', '-f', compose_file] + services + ['-p', project_name]

    msg = click.style('[VERBOSE] ', fg='green')
    msg += 'Compose command: ' + ' '.join(base_cmd + list(command))
    click.echo(msg, err=True)
    subprocess.call(base_cmd + list(command))


def add_services_from_plugins(available_services: list):
    """Read plugin path and extract services in subdirectories services/"""

    from pkg_resources import iter_entry_points

    # Override services with plugins
    for entry in iter_entry_points('stakkr.plugins'):
        plugin_dir = str(entry).split('=')[0].strip()
        services_dir = package_utils.get_venv_basedir() + '/plugins/' + plugin_dir + '/services'

        conf_files = _get_services_from_dir(services_dir)
        for conf_file in conf_files:
            available_services[conf_file[:-4]] = services_dir + '/' + conf_file

    return available_services


def add_local_services(available_services: list):
    """Get services in the virtualenv services/ directory, so specific to that stakkr"""

    services_dir = package_utils.get_venv_basedir() + '/services'

    conf_files = _get_services_from_dir(services_dir)
    for conf_file in conf_files:
        available_services[conf_file[:-4]] = services_dir + '/' + conf_file

    return available_services


def get_available_services():
    """Get standard services bundled with stakkr"""

    services_dir = package_utils.get_dir('static') + '/services/'
    conf_files = _get_services_from_dir(services_dir)

    services = dict()
    for conf_file in conf_files:
        services[conf_file[:-4]] = services_dir + conf_file

    return services


def get_enabled_services(configured_services: list):
    """Compile all available services : standard, plugins, local install"""

    available_services = get_available_services()
    available_services = add_services_from_plugins(available_services)
    available_services = add_local_services(available_services)

    services_files = []
    for service in configured_services:
        if service not in available_services:
            msg = 'Error: service "{}" has no configuration file. '.format(service)
            msg += 'Check your compose.ini'
            click.secho(msg, fg='red')
            sys.exit(1)
        services_files.append(available_services[service])

    return services_files

def get_configured_services(config_file: str = None):
    """Get services set in compose.ini"""

    configured_services = get_main_config(config_file).get('services')
    return configured_services


def get_main_config(config: str):
    """Read main compose.ini file"""

    config = Config(config)
    main_config = config.read()

    if main_config is False:
        config.display_errors()
        sys.exit(1)

    return main_config['main']


def set_env_values_from_conf(config: list):
    """Define environment variables to be used in services yaml"""

    os.environ['DOCKER_UID'] = _get_uid(config.pop('uid'))
    os.environ['DOCKER_GID'] = _get_gid(config.pop('gid'))
    os.environ['COMPOSE_BASE_DIR'] = package_utils.get_venv_basedir()

    for parameter, value in config.items():
        parameter = 'DOCKER_{}'.format(parameter.replace('.', '_').upper())
        os.environ[parameter] = str(value)


def _get_services_from_dir(services_dir: str):
    if os.path.isdir(services_dir) is False:
        return []

    return [service for service in os.listdir(services_dir) if service.endswith('.yml')]


def _get_uid(uid: int):
    if uid is not None:
        return str(uid)

    return '1000' if os.name == 'nt' else str(os.getuid())


def _get_gid(gid: int):
    if gid is not None:
        return str(gid)

    return '1000' if os.name == 'nt' else str(os.getgid())


if __name__ == '__main__':
    cli()
