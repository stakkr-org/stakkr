import click
import os
import subprocess
import sys

from stakkr import package_utils
from stakkr.configreader import Config
verbose = click.style('[VERBOSE] ', fg='green')


@click.command(help="Wrapper for docker-compose", context_settings=dict(ignore_unknown_options=True))
@click.option('--config', '-c', help="Override the conf/compose.ini")
@click.argument('command', nargs=-1, type=click.UNPROCESSED)
def cli(config: str, command):
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

    # _dump_compose_config(base_cmd, project_name)

    click.echo(verbose + 'Compose command: ' + ' '.join(base_cmd + list(command)), err=True)
    subprocess.call(base_cmd + list(command))


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


def get_enabled_services(configured_services: list):
    # Services available from base and plugins
    available_services = get_available_services()
    available_services = add_services_from_plugins(available_services)
    available_services = add_local_services(available_services)

    services_files = []
    for service in configured_services:
        if service not in available_services:
            print(click.style('Error: service "{}" has no configuration file. Check your compose.ini'.format(service), fg='red'))
            sys.exit(1)
        services_files.append(available_services[service])

    return services_files

def get_configured_services(config_file: str = None):
    # Services configured in the given config file. 
    configured_services = get_main_config(config_file).get('services')
    return configured_services

def get_main_config(config: str):
    config = Config(config)
    main_config = config.read()

    if main_config is False:
        config.display_errors()
        sys.exit(1)

    return main_config['main']


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


# def _dump_compose_config(base_cmd: list, project_name: str):
    # import tempfile

    # tmpdir = '{}/stakkr/{}'.format(tempfile.gettempdir(), project_name)
    # os.putenv('TMP_COMPOSE_CONFIG_DIR', tmpdir)
    # try:
        # os.makedirs(tmpdir)
    # except:
        # pass

    # with open(tmpdir + '/docker-compose.yml', 'w') as file:
        # file.write(subprocess.check_output(base_cmd + ['config']).decode())


if __name__ == '__main__':
    cli()
