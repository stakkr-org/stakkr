# coding: utf-8
"""Simple Config Reader."""

from os import path
from sys import stderr
import anyconfig
from stakkr.file_utils import get_file, find_project_dir
from yaml import FullLoader


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
        """Display errors in STDERR."""
        from click import style

        msg = 'Failed validating config ('
        msg += ', '.join(self.config_files)
        msg += '):\n    - {}\n'.format(self.error)
        msg += '\nMake sure you have the right services.\n'
        stderr.write(style(msg, fg='red'))

    def read(self):
        """
        Parse the configs and validate it.

        It could be either local or from a local services
        (first local then packages by alphabetical order).
        """
        spec = {}
        for filepath in self.spec_files:
            yaml = anyconfig.load(filepath, Loader=FullLoader)
            spec = _merge_dictionaries(spec, yaml)
        # Waiting anyconfig to work for that :
        # schema = anyconfig.load(self.spec_files, Loader=FullLoader)

        conf = {}
        for filepath in self.config_files:
            yaml = anyconfig.load(filepath, Loader=FullLoader)
            conf = _merge_dictionaries(conf, yaml)
        # Waiting anyconfig to work for that :
        # config = anyconfig.load(self.spec_files, Loader=FullLoader)

        # Make sure the compiled configuration is valid
        valid, errs = anyconfig.validate(conf, spec, ac_schema_safe=False, ac_schema_errors=True)
        if valid is False:
            self.error = errs[0]
            return False

        conf['project_dir'] = path.realpath(path.dirname(self.config_file))
        if conf['project_name'] == '':
            conf['project_name'] = path.basename(conf['project_dir'])

        return conf

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
        return path.abspath(config_file), path.dirname(config_file)

    project_dir = find_project_dir()
    return '{}/stakkr.yml'.format(project_dir), project_dir


def _merge_dictionaries(dict1, dict2):
    for key, val in dict1.items():
        if isinstance(val, dict):
            dict2_node = dict2.setdefault(key, {})
            _merge_dictionaries(val, dict2_node)

        else:
            if key not in dict2:
                dict2[key] = val

    return dict2
