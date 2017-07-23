import os

from click import style
from configobj import ConfigObj, flatten_errors
from stakkr import package_utils
from validate import Validator


class Config():
    """Config Parser of Stakkr. Set default values and validate conf/compose.ini
    with conf/configspec.ini"""

    def __init__(self):
        self.config_file = package_utils.get_venv_basedir() + '/conf/compose.ini'


    def read(self):
        """Read the default values and overriden ones"""

        if os.path.isfile(self.config_file) is False:
            msg = 'Error: Missing "' + self.config_file + '". '
            if self.config_file.endswith('.ini'):
                msg += 'Read the doc and create it'
            else:
                msg += 'Please restore it.'
            raise IOError(msg)

        return self._parse()


    def _display_errors(self, config: dict, validated):
        print(style('Failed validating your conf/config.ini: ', fg='red'))
        for [sectionList, key, error] in flatten_errors(config, validated):
            if key is not None:
                error = 'Missing' if error is False else str(error)
                print('  - "{}" : {}'.format(style(key, fg='yellow'), error))
        exit(1)


    def _parse(self):
        """Parse the config from configspecs that is a file either local or from a package"""

        config = ConfigObj(infile=self.config_file, configspec=package_utils.get_file('static', 'configspec.ini'))

        validator = Validator()
        validated = config.validate(validator, preserve_errors=True)
        if validated is not True:
            self._display_errors(config, validated)

        return config
