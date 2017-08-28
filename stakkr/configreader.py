# -*- coding: utf-8 -*-
"""Simple Config Reader"""

import os
import sys
from configobj import ConfigObj, flatten_errors
from validate import Validator
from stakkr import package_utils


class Config():
    """Parser of Stakkr. Set default values and validate
    conf/compose.ini with conf/configspec.ini
    """

    def __init__(self, config_file: str = None):
        """If no config given, read the default one"""
        self.errors = dict()
        self.config_file = package_utils.get_venv_basedir() + '/conf/compose.ini'
        if config_file is not None:
            self.config_file = config_file


    def display_errors(self):
        """Display errors in STDOUT"""
        from click import style

        print(style('Failed validating {}: '.format(self.config_file), fg='red'), file=sys.stderr)
        for key, error in self.errors.items():
            print('  - "{}" : {}'.format(style(key, fg='yellow'), error), file=sys.stderr)


    def read(self):
        """Read the default values and overriden ones"""
        if os.path.isfile(self.config_file) is False:
            raise IOError('Config file {} does not exist'.format(self.config_file))

        return self._parse()


    def _parse(self):
        """Parse the config from configspecs that is a file either local or from a package"""

        config_spec_file = package_utils.get_file('static', 'configspec.ini')
        config = ConfigObj(infile=self.config_file, configspec=config_spec_file)

        validator = Validator()
        validated = config.validate(validator, preserve_errors=True)
        if validated is not True:
            self._register_errors(config, validated)
            return False

        return config


    def _register_errors(self, config: dict, validated):
        for [section_list, key, error] in flatten_errors(config, validated):
            if key is not None:
                error = 'Missing' if error is False else str(error)
                self.errors[key] = error
