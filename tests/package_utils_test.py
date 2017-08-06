import os
import sys
import unittest

from distutils.sysconfig import get_config_vars
from stakkr import package_utils as pu

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


# https://docs.python.org/3/library/unittest.html#assert-methods
class PackageUtilsTest(unittest.TestCase):
    def test_venv_basedir(self):
        """Make sure, even in another directory, the venv base dir is correct"""
        venv_base = pu.get_venv_basedir()

        self.assertEqual(os.path.abspath(get_config_vars()['exec_prefix'] + '/../'), venv_base)
