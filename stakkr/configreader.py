# coding: utf-8
"""Simple Config Reader."""

from collections.abc import Iterable
from os import path
from sys import stderr
import anyconfig
from jsonschema.exceptions import _Error
from stakkr.file_utils import get_file, find_project_dir


class Config:
    """
    Parser of Stakkr.

    Set default values and validate stakkr.yml with specs
    """

    def __init__(self, config_file: str):
        """
        Build list of files to validate a config, set default values
        Then the given config file
        """
        self.config_file, self.project_dir = get_config_and_project_dir(config_file)
        self._build_config_files_list()
        self._build_config_schemas_list()
        self.error = ''

    def display_errors(self):
        """Display errors in STDOUT."""
        from click import style

        msg = 'Failed validating config ('
        msg += ', '.join(self.config_files)
        msg += '):\n    - {}\n'.format(self.error)
        stderr.write(style(msg, fg='red'))

    def read(self):
        """
        Parse the configs and validate it.

        It could be either local or from a local services
        (first local then packages by alphabetical order).
        """
        schema = anyconfig.multi_load(self.spec_files)
        config = anyconfig.multi_load(self.config_files)
        # Make sure the compiled configuration is valid
        try:
            anyconfig.validate(config, schema, safe=False)
        except _Error as error:
            self.error = '{} ({})'.format(error.message, ' -> '.join(map(str, error.path)))
            return False

        config['project_dir'] = path.realpath(path.dirname(self.config_file))
        if config['project_name'] == '':
            config['project_name'] = path.basename(config['project_dir'])

        return config

    def _build_config_files_list(self):
        self.config_files = [
            # Stakkr default config
            get_file('static', 'config_default.yml'),
            '{}/services/*/config_default.yml'.format(self.project_dir)]
        # Stakkr main config file finally with user's values
        self.config_files += [self.config_file]

    def _build_config_schemas_list(self):
        self.spec_files = [
            # Stakkr config validation
            get_file('static', 'config_schema.yml'),
            '{}/services/*/config_schema.yml'.format(self.project_dir)]


def get_config_and_project_dir(config_file: str):
    """Guess config file name and project dir"""
    if config_file is not None:
        config_file = path.abspath(config_file)
        project_dir = path.dirname(config_file)
    else:
        project_dir = find_project_dir()
        config_file = '{}/stakkr.yml'.format(project_dir)

    return config_file, project_dir
