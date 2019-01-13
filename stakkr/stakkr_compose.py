#!/usr/bin/env python
# coding: utf-8
"""
CLI Main Entry Point.

Wraps docker-compose and build it from what has been taken from config.
"""

import glob
import os
import subprocess
import sys
import click
from stakkr import file_utils
from stakkr.configreader import Config


@click.command(help="Wrapper for docker-compose",
               context_settings=dict(ignore_unknown_options=True))
@click.option('--config-file', '-c', help="Set stakkr config file location (default stakkr.yml)")
@click.argument('command', nargs=-1, type=click.UNPROCESSED)
def cli(config_file: str = None, command: tuple = ()):
    """Command line entry point."""
    config, config_file = _get_config(config_file)

    # Set main config and services as env variables
    _set_env_from_config(config)

    # Register proxy env parameters
    _set_env_for_proxy(config['proxy'])

    # set the base command
    base_cmd = _get_base_command(config)

    msg = click.style('[VERBOSE] ', fg='green')
    msg += 'Compose command: ' + ' '.join(base_cmd + list(command))
    click.echo(msg, err=True)
    subprocess.call(base_cmd + list(command))


def _add_local_services(project_dir: str, available_services: list):
    """Get services in the virtualenv services/ directory, so specific to that stakkr."""
    services_dir = project_dir + '/services/*/docker-compose'
    for service_dir in glob.glob(services_dir):
        conf_files = _get_services_from_dir(service_dir)
        for conf_file in conf_files:
            available_services[conf_file[:-4]] = service_dir + '/' + conf_file

    return available_services


def get_available_services(project_dir: str):
    """Get standard services bundled with stakkr."""
    services_dir = file_utils.get_dir('static') + '/services/'
    conf_files = _get_services_from_dir(services_dir)

    services = dict()
    for conf_file in conf_files:
        services[conf_file[:-4]] = services_dir + conf_file

    services = _add_local_services(project_dir, services)

    return services


def _get_base_command(config: dict):
    """Build the docker-compose file to be run as a command."""
    main_file = 'docker-compose.yml'
    # Set the network subnet ?
    if config['subnet'] != '':
        main_file = 'docker-compose.subnet.yml'
    cmd = ['docker-compose', '-f', file_utils.get_file('static', main_file)]

    # What to load
    activated_services = _get_enabled_services_files(
        config['project_dir'],
        [svc for svc, opts in config['services'].items() if opts['enabled'] is True])
    # Create the command
    services = []
    for service in activated_services:
        services.append('-f')
        services.append(service)

    return cmd + services + ['-p', config['project_name']]


def _get_config(config_file: str):
    """Read main stakkr.yml file."""
    config_reader = Config(config_file)
    config = config_reader.read()

    if config is False:
        config.display_errors()
        sys.exit(1)

    return config, config_reader.config_file


def _get_enabled_services_files(project_dir: str, configured_services: list):
    """Compile all available services : standard and local install."""
    available_services = get_available_services(project_dir)

    services_files = []
    for service in configured_services:
        if service not in available_services:
            msg = 'Error: service "{}" has no configuration file. '.format(service)
            msg += 'Check your config'
            click.secho(msg, fg='red')
            sys.exit(1)
        services_files.append(available_services[service])

    return services_files


def _get_gid(gid: int):
    if gid is not None:
        return str(gid)

    return '1000' if os.name == 'nt' else str(os.getgid())


def _get_services_from_dir(services_dir: str):
    if os.path.isdir(services_dir) is False:
        return []

    return [service for service in os.listdir(services_dir) if service.endswith('.yml')]


def _get_uid(uid: int):
    if uid is not None:
        return str(uid)

    return '1000' if os.name == 'nt' else str(os.getuid())


def _set_env_for_proxy(config: dict):
    """Define environment variables to be used in services yaml."""
    os.environ['PROXY_ENABLED'] = str(config['enabled'])
    os.environ['PROXY_DOMAIN'] = str(config['domain'])


def _set_env_for_services(services: dict):
    for service, params in services.items():
        if params['enabled'] is False:
            continue

        for param, value in params.items():
            env_var = 'DOCKER_{}_{}'.format(service, param).upper()
            os.environ[env_var] = str(value)


def _set_env_from_config(config: dict):
    """Define environment variables to be used in services yaml."""
    os.environ['COMPOSE_BASE_DIR'] = config['project_dir']
    os.environ['COMPOSE_PROJECT_NAME'] = config['project_name']
    for parameter, value in config.items():
        if parameter == 'services':
            _set_env_for_services(value)
            continue

        os.environ['DOCKER_{}'.format(parameter.upper())] = str(value)

    # Do that at the end, else the value in config will overwrite the possible
    # default value
    os.environ['DOCKER_UID'] = _get_uid(config['uid'])
    os.environ['DOCKER_GID'] = _get_gid(config['gid'])


if __name__ == '__main__':
    cli()
