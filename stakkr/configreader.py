# coding: utf-8
"""Simple Config Reader."""

import anyconfig
from sys import stderr
from jsonschema.exceptions import _Error
from stakkr.package_utils import get_file, find_project_dir
from os import path


class Config:
    """
    Parser of Stakkr.

    Set default values and validate conf/compose.ini with conf/configspec.ini.
    """

    def __init__(self, config_file: str):
        """
        Build list of files to validate a config, set default values
        Then the given config file
        """
        self.project_dir = find_project_dir()
        self.config_file = '{}/stakkr.yml'.format(self.project_dir) if config_file is None else config_file
        self._build_config_files_list()
        self._build_config_schemas_list()
        self.error = ''

    def display_errors(self):
        """Display errors in STDOUT."""
        from click import style

        msg = 'Failed validating main config or plugin configs ('
        msg += ', '.join(self.config_files)
        msg += '):\n    - {}'.format(self.error)
        print(style(msg, fg='red'), file=stderr)

    def read(self):
        """
        Parse the configs and validate it.

        It could be either local or from a plugin or local services
        (first local then packages by alphabetical order).
        """
        schema = anyconfig.multi_load(self.spec_files)
        config = anyconfig.multi_load(self.config_files)
        # Make sure the compiled configuration is valid
        try:
            anyconfig.validate(config, schema, safe=False)
        except _Error as error:
            self.error = '{} ({})'.format(error.message, ' -> '.join(error.path))
            return False

        config['project_dir'] = path.dirname(self.config_file)

        if config['project_name'] == '':
            config['project_name'] = path.basename(config['project_dir'])

        return config

    def _build_config_files_list(self):
        self.config_files = [
            # Stakkr default config
            get_file('static', 'config_default.yml'),
            # plugins default config
            '{}/plugins/*/config_default.yml'.format(self.project_dir),
            '{}/services/*/config_default.yml'.format(self.project_dir)]
        # Stakkr main config file finally with user's values
        self.config_files += [self.config_file]

    def _build_config_schemas_list(self):
        self.spec_files = [
            # Stakkr config validation
            get_file('static', 'config_schema.yml'),
            # plugins config validation
            '{}/plugins/*/config_schema.yml'.format(self.project_dir),
            '{}/services/*/config_schema.yml'.format(self.project_dir)]
