from configparser import ConfigParser
import os


class Config():
    def __init__(self, config_file):
        self.config_file = config_file

    def read(self):
        if os.path.isfile(self.config_file) is False:
            msg = 'Error: Missing ' + self.config_file + ' '
            msg += 'Create it and override values from ' + self.config_file + '.tpl'
            raise IOError(msg)

        return self.__parse()

    def __parse(self):
        config = ConfigParser()
        config.read(self.config_file)
        return config
