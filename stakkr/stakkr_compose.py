#!/usr/bin/env python
# coding: utf-8
"""
CLI Main Entry Point.

Wraps docker-compose and build it from what has been taken from config.
"""

import os
import subprocess
import sys
import click
from stakkr import package_utils
from stakkr.configreader import Config


@click.command(help="Wrapper for docker-compose",
               context_settings=dict(ignore_unknown_options=True))
@click.option('--config-file', '-c', help="Set stakkr config file location (default stakkr.yml)")
@click.argument('command', nargs=-1, type=click.UNPROCESSED)
def cli(config_file: str, command):
    """Command line entry point."""
    config = get_config(config_file)
    set_env_from_config(config)

    # Register proxy env parameters
    set_env_for_proxy(config['proxy'])

    # Get info for the project
    project_dir = package_utils.find_project_dir()
    project_name = config['project_name']
    if project_name == '':
        project_name = os.path.basename(project_dir)
    os.putenv('COMPOSE_PROJECT_NAME', project_name)

    # set the base command
    base_cmd = get_base_command(project_name, config)

    msg = click.style('[VERBOSE] ', fg='green')
    msg += 'Compose command: ' + ' '.join(base_cmd + list(command))
    click.echo(msg, err=True)
    subprocess.call(base_cmd + list(command))


def add_services_from_plugins(available_services: list):
    """Read plugin path and extract services in subdirectories services/."""
    from pkg_resources import iter_entry_points

    # Override services with plugins
    for entry in iter_entry_points('stakkr.plugins'):
        plugin_dir = str(entry).split('=')[0].strip()
        services_dir = package_utils.find_project_dir() + '/plugins/' + plugin_dir + '/services'

        conf_files = _get_services_from_dir(services_dir)
        for conf_file in conf_files:
            available_services[conf_file[:-4]] = services_dir + '/' + conf_file

    return available_services


def add_local_services(available_services: list):
    """Get services in the virtualenv services/ directory, so specific to that stakkr."""
    services_dir = package_utils.find_project_dir() + '/services'
    conf_files = _get_services_from_dir(services_dir)
    for conf_file in conf_files:
        available_services[conf_file[:-4]] = services_dir + '/' + conf_file

    return available_services


def get_available_services():
    """Get standard services bundled with stakkr."""
    services_dir = package_utils.get_dir('static') + '/services/'
    conf_files = _get_services_from_dir(services_dir)

    services = dict()
    for conf_file in conf_files:
        services[conf_file[:-4]] = services_dir + conf_file

    services = add_services_from_plugins(services)
    services = add_local_services(services)

    return services


def get_base_command(project_name: str, config: dict):
    """Build the docker-compose file to be run as a command."""
    main_file = 'docker-compose.yml'
    # Set the network subnet ?
    if config['subnet'] != '':
        main_file = 'docker-compose.subnet.yml'
    cmd = ['docker-compose', '-f', package_utils.get_file('static', main_file)]

    # What to load
    activated_services = get_enabled_services_files(
        [svc for svc, opts in config['services'].items() if opts['enabled'] is True])
    # Create the command
    services = []
    for service in activated_services:
        services.append('-f')
        services.append(service)

    return cmd + services + ['-p', project_name]


def get_enabled_services_files(configured_services: list):
    """Compile all available services : standard, plugins, local install."""
    available_services = get_available_services()

    services_files = []
    for service in configured_services:
        if service not in available_services:
            msg = 'Error: service "{}" has no configuration file. '.format(service)
            msg += 'Check your config'
            click.secho(msg, fg='red')
            sys.exit(1)
        services_files.append(available_services[service])

    return services_files


def get_configured_services(config_file: str = None):
    """Get services set in compose.ini."""
    configured_services = get_config(config_file)['main'].get('services')
    return configured_services


def get_config(config_file: str):
    """Read main stakkr.yml file."""
    config = Config(config_file).read()

    if config is False:
        config.display_errors()
        sys.exit(1)

    return config


def set_env_from_config(config: list):
    """Define environment variables to be used in services yaml."""
    os.environ['DOCKER_UID'] = _get_uid(config['uid'])
    os.environ['DOCKER_GID'] = _get_gid(config['gid'])
    os.environ['COMPOSE_BASE_DIR'] = package_utils.find_project_dir()

    for parameter, value in config.items():
        if parameter == 'services':
            set_env_for_services(value)
            continue

        os.environ['DOCKER_{}'.format(parameter.upper())] = str(value)


def set_env_for_proxy(config: list):
    """Define environment variables to be used in services yaml."""
    os.environ['PROXY_ENABLED'] = str(config['enabled'])
    os.environ['PROXY_DOMAIN'] = str(config['domain'])
    os.environ['PROXY_PORT'] = str(config['port'])


def set_env_for_services(services: dict):
    for service, params in services.items():
        if params['enabled'] is False:
            continue

        for param, value in params.items():
            env_var = 'DOCKER_{}_{}'.format(service, param).upper()
            os.environ[env_var] = str(value)


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
