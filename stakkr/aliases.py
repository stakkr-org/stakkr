# coding: utf-8
"""Aliases management"""

from argparse import ArgumentParser
from yaml import load, error
from stakkr.configreader import get_config_and_project_dir


class StakkrArgumentParser(ArgumentParser):
    """Own Argument Parser to avoid options"""
    def error(self, msg):
        pass


def get_aliases():
    """Get aliases from config file"""
    parser = StakkrArgumentParser()
    parser.add_argument('-c')
    args = vars(parser.parse_args())
    config_file, _ = get_config_and_project_dir(args['c'])
    config = {}
    try:
        with open(config_file, 'r') as stream:
            config = load(stream)
    except (error.YAMLError, FileNotFoundError):
        pass

    return config['aliases'] if 'aliases' in config else {}
