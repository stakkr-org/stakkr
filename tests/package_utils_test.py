import os
import sys
import unittest

from distutils.sysconfig import get_python_lib
from stakkr import package_utils as pu

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


# https://docs.python.org/3/library/unittest.html#assert-methods
class PackageUtilsTest(unittest.TestCase):
    def test_venv_basedir(self):
        """Make sure, even in another directory, the venv base dir is correct"""
        venv_base = pu.get_venv_basedir()

        self.assertEqual(os.path.abspath(get_python_lib() + '/../../../../'), venv_base)

    def test_get_dir_abspath(self):
        """Make sure the path of a dir is returned"""
        dir_path = pu.get_dir('tpls')

        self.assertEqual(os.path.abspath(get_python_lib() + '/stakkr/tpls'), dir_path)


    def test_get_file_abspath(self):
        """Make sure the path of a file is returned"""
        file_path = pu.get_file('tpls', '.env')

        self.assertEqual(os.path.abspath(get_python_lib() + '/stakkr/tpls/.env'), file_path)
