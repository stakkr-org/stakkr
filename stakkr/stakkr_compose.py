import click
import os
import sys

from stakkr import package_utils
from stakkr.configreader import Config
from subprocess import Popen


@click.command(help="Wrapper for docker-compose", context_settings=dict(ignore_unknown_options=True))
@click.option('--config', '-c', help="Override the conf/compose.ini")
@click.argument('command', nargs=-1, type=click.UNPROCESSED)
def cli(config: str, command):
    config = Config(config)
    user_config_main = config.read()
    if user_config_main is False:
        config.display_errors()
        sys.exit(1)

    user_config_main = user_config_main['main']
    set_env_values_from_conf(user_config_main)

    project_name = user_config_main.get('project_name')
    os.putenv('COMPOSE_PROJECT_NAME', project_name)

    # Services from config
    configured_services = user_config_main.get('services')

    # Services available from base and plugins
    available_services = get_available_services()
    available_services = add_services_from_plugins(available_services)
    available_services = add_local_services(available_services)
    services = get_enabled_services(configured_services, available_services)

    cmd = ['docker-compose', '-f', package_utils.get_file('static', 'docker-compose.yml')] + services
    cmd += ['-p', project_name] + list(command)

    Popen(cmd)


def add_services_from_plugins(available_services: list):
    from pkg_resources import iter_entry_points

    # Override services with plugins
    for entry in iter_entry_points('stakkr.plugins'):
        plugin_dir = str(entry).split('=')[0].strip()
        services_dir = package_utils.get_venv_basedir() + '/plugins/' + plugin_dir + '/services'

        conf_files = _get_services_from_dir(services_dir)
        if conf_files is []:
            continue

        for conf_file in conf_files:
            available_services[conf_file[:-4]] = services_dir + '/' + conf_file

    return available_services


def add_local_services(available_services: list):
    services_dir = package_utils.get_venv_basedir() + '/services'

    conf_files = _get_services_from_dir(services_dir)
    for conf_file in conf_files:
        available_services[conf_file[:-4]] = services_dir + '/' + conf_file

    return available_services


def get_available_services():
    services_dir = package_utils.get_dir('static') + '/services/'
    conf_files = _get_services_from_dir(services_dir)

    services = dict()
    for conf_file in conf_files:
        services[conf_file[:-4]] = services_dir + conf_file

    return services


def get_enabled_services(configured_services: list, available_services: list):
    services_files = []
    for service in configured_services:
        if service not in available_services:
            print(click.style('Error: service "{}" has no configuration file. Check your compose.ini'.format(service), fg='red'))
            sys.exit(1)
        services_files.append('-f')
        services_files.append(available_services[service])

    return services_files


def set_env_values_from_conf(config: list):
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
