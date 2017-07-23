import io
import os
import re
import subprocess
import sys
import unittest

from contextlib import redirect_stdout, redirect_stderr
from stakkr import package_utils
from stakkr.configreader import Config

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


# https://docs.python.org/3/library/unittest.html#assert-methods
class ConfigReaderTest(unittest.TestCase):
    def test_bad_config(self):
        """Test a non existing configuration file"""
        c = Config('/does/not/exists')
        with self.assertRaisesRegex(IOError, "Config file /does/not/exists does not exist"):
            c.read()


    def test_default_config(self):
        """Test the default config (exit if it exists)"""
        if os.path.isfile(package_utils.get_venv_basedir() + '/conf/compose.ini'):
            return

        c = Config()
        with self.assertRaisesRegex(IOError, "Config file .*compose.ini does not exist"):
            c.read()


    def test_invalid_config(self):
        """Test an existing configuration file but invalid"""
        import re

        c = Config(base_dir + '/static/config_invalid.ini')
        self.assertFalse(c.read())
        self.assertGreater(len(c.errors), 0)
        self.assertTrue('project_name' in c.errors)
        self.assertEqual('Missing', c.errors['project_name'])
        self.assertTrue('php.version' in c.errors)
        self.assertEqual('the value "8.0" is unacceptable.', c.errors['php.version'])
        f = io.StringIO()
        with redirect_stdout(f):
            c.display_errors()
        res = f.getvalue()

        regex = re.compile('Failed validating .*config_invalid.ini', re.MULTILINE)
        self.assertRegex(res, regex)

        regex = re.compile('the value ".*8.0.*" is unacceptable', re.MULTILINE)
        self.assertRegex(res, regex)


    def test_valid_config(self):
        """Test an existing and valid configuration file"""
        from configobj import ConfigObj

        c = Config(base_dir + '/static/config_valid.ini')
        config = c.read()
        self.assertIs(ConfigObj, type(config))
        self.assertTrue('main' in config)
        self.assertTrue('services' in config['main'])
        self.assertTrue('php' in config['main']['services'])
        self.assertFalse('apache' in config['main']['services'])

        self.assertTrue('project_name' in config['main'])
        self.assertEqual('test', config['main']['project_name'])

        self.assertTrue('php.version' in config['main'])
        self.assertEqual('7.0', config['main']['php.version'])


if __name__ == "__main__":
    unittest.main()
