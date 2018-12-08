from os import chdir, getcwd
from os.path import abspath, dirname, realpath
import sys
import unittest

from stakkr import file_utils

base_dir = abspath(dirname(__file__))
sys.path.insert(0, base_dir + '/../')


# https://docs.python.org/3/library/unittest.html#assert-methods
class FilesUtilsTest(unittest.TestCase):
    def test_get_lib_basedir(self):
        self.assertEquals(
            dirname(dirname(realpath(__file__))) + '/stakkr',
            file_utils.get_lib_basedir())

    def test_get_dir(self):
        self.assertEquals(
            dirname(dirname(realpath(__file__))) + '/stakkr/static',
            file_utils.get_dir('static'))

    def test_get_file(self):
        self.assertEquals(
            dirname(dirname(realpath(__file__))) + '/stakkr/static/config_default.yml',
            file_utils.get_dir('static/config_default.yml'))

    def test_find_project_dir_from_root(self):
        static_path = dirname(realpath(__file__)) + '/static'
        chdir(static_path)
        self.assertEquals(static_path, file_utils.find_project_dir())

    def test_find_project_dir_from_subdir(self):
        static_path = dirname(realpath(__file__)) + '/static'
        chdir(static_path + '/home')
        self.assertEquals(static_path, file_utils.find_project_dir())


if __name__ == "__main__":
    unittest.main()
