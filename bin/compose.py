#!/usr/bin/python3
from argparse import ArgumentParser
from configparser import ConfigParser
from subprocess import call
import os
import sys


MAIN_CONFIGURATION_FILE = 'conf/compose.ini'


def read_mainconf_or_exit():
    """Check if the configuration file exists"""
    if os.path.isfile(MAIN_CONFIGURATION_FILE) is False:
        print("Error: Missing " + MAIN_CONFIGURATION_FILE)
        print("Create it and override values from " + MAIN_CONFIGURATION_FILE + ".tpl")
        sys.exit(1)

    return parse_config()


def parse_config():
    config = ConfigParser()
    config.read(MAIN_CONFIGURATION_FILE)
    return config


def set_env_values_from_conf(config: list):
    os.putenv('DOCKER_UID', str(config.get('uid', os.getuid())))
    os.putenv('DOCKER_GID', str(config.get('gid', os.getgid())))
    os.putenv('DOCKER_HOSTNAME', str(config.get('hostname', 'localhost')))

    # Services versions and options
    os.putenv('DOCKER_APACHE_PORT', str(config.get('apache.port', 80)))
    os.putenv('DOCKER_APACHE_VERSION', str(config.get('apache.version', 2.2)))

    os.putenv('DOCKER_PHP_VERSION', str(config.get('php.version', 5.6)))

    os.putenv('DOCKER_MONGO_VERSION', str(config.get('mongo.version', 3.3)))

    os.putenv('DOCKER_MYSQL_VERSION', str(config.get('mysql.version', 5.7)))
    os.putenv('DOCKER_MYSQL_ROOT_PASSWORD', str(config.get('mysql.root_password', 'changeme')))

    os.putenv('DOCKER_ELASTICSEARCH_VERSION', str(config.get('elasticsearch.version', 2)))


def get_cli_arguments():
    arg_parser = ArgumentParser(description="Process the only argument expected (The command)")
    arg_parser.add_argument('command', help='Command for docker-compose')
    args = arg_parser.parse_args()
    command = [args.command]
    if (args.command == 'up'):
        command.append('-d')

    return command


def get_services(services: list):
    services_files = []
    for service in services:
        service_file = 'service/' + service + '.yml'
        if os.path.isfile(service_file) is False:
            print('Error: service ' + service + ' is invalid')
            sys.exit(1)
        services_files.append('-f')
        services_files.append(service_file)

    return services_files


if __name__ == '__main__':
    config = read_mainconf_or_exit()

    main_config = config['main']
    set_env_values_from_conf(main_config)

    project_name = str(main_config.get('project_name', 'inet' + os.path.basename(os.getcwd()).replace('-', '')))
    cmd = ['docker-compose', '-f', 'docker-compose.yml']
    # get the services from an array that has been filtered to remove the empty values
    cmd += get_services([service for service in main_config.get('services', '').split(',') if service != ''])
    cmd += ['-p', project_name] + get_cli_arguments()
    call(cmd)
