# coding: utf-8
"""Aliases management"""

from sys import argv
from yaml import load, error
from stakkr.configreader import get_config_and_project_dir


def get_config_from_argv(argv: list):
    """Search for a config file option in command line"""
    for index, arg in enumerate(argv):
        # manage "=" sign
        if arg.find('=') != -1 and arg.split('=')[0] == '--config':
            return arg.split('=')[1]

        # else search for -c  or --config and get the next value
        if arg in ['-c', '--config']:
            try:
                return argv[index + 1]
            except IndexError:
                raise ValueError('You must specify the config file name')

    return None


def get_aliases():
    """Get aliases from config file"""
    config_file, _ = get_config_and_project_dir(get_config_from_argv(argv[1:]))
    config = {}
    try:
        with open(config_file, 'r') as stream:
            config = load(stream)
    except (error.YAMLError, FileNotFoundError):
        pass

    return config['aliases'] if 'aliases' in config else {}
