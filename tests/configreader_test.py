#!/usr/bin/env python
import os
import re
import sys
import unittest
import pytest
from stakkr.configreader import Config
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


# https://docs.python.org/3/library/unittest.html#assert-methods
class ConfigReaderTest(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd

    def test_bad_config(self):
        """Test a non existing configuration file"""
        c = Config('/does/not/exists.yml')
        with self.assertRaisesRegex(IOError, "No such file or directory: '/does/not/exists.yml'"):
            c.read()

    def test_invalid_config(self):
        """Test an existing configuration file but invalid"""

        c = Config(base_dir + '/static/config_invalid.yml')
        self.assertFalse(c.read())

        self.assertGreater(len(c.error), 0)
        self.assertRegex(c.error, '.*Additional properties are not allowed.*')

        c.display_errors()
        out, err = self.capfd.readouterr()

        regex = re.compile(
            'Failed validating config.+config_default.yml.+config_invalid.yml.*',
            re.MULTILINE)
        self.assertRegex(err, regex)

        regex = re.compile('Additional properties are not allowed.*', re.MULTILINE)
        self.assertRegex(err, regex)

    def test_valid_config(self):
        """Test an existing and valid configuration file"""
        c = Config(base_dir + '/static/stakkr.yml')
        config = c.read()
        self.assertIs(dict, type(config))
        self.assertTrue('services' in config)

        self.assertTrue('php' in config['services'])
        self.assertTrue('version' in config['services']['php'])
        self.assertTrue('enabled' in config['services']['php'])
        self.assertEqual(7.2, config['services']['php']['version'])
        self.assertTrue(config['services']['php']['enabled'])

        self.assertTrue('apache' not in config['services'])

        self.assertTrue('project_name' in config)
        self.assertEqual('static', config['project_name'])

    def test_valid_config_no_project(self):
        """Test an existing and valid configuration file"""
        c = Config(base_dir + '/static/config_valid_network.yml')
        config = c.read()
        self.assertIs(dict, type(config))
        self.assertTrue('services' in config)

        self.assertTrue('project_name' in config)
        self.assertEqual('testnet', config['project_name'])


if __name__ == "__main__":
    unittest.main()
