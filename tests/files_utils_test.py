from os import chdir
from os.path import abspath, dirname, isdir, isfile, realpath
import sys
import unittest

from stakkr import file_utils

BASE_DIR = abspath(dirname(__file__))
sys.path.insert(0, BASE_DIR + '/../')


class FilesUtilsTest(unittest.TestCase):
    def test_get_lib_basedir(self):
        dir = file_utils.get_lib_basedir()
        self.assertTrue(isdir(dir))
        self.assertTrue(isfile(dir + '/stakkr_compose.py'))

    def test_get_dir(self):
        dir = file_utils.get_dir('static')
        self.assertTrue(isdir(dir))
        self.assertTrue(isfile(dir + '/docker-compose.yml'))

    def test_get_file(self):
        file = file_utils.get_dir('static/config_default.yml')
        self.assertTrue(isfile(file))

    def test_find_project_dir_from_root(self):
        static_path = dirname(realpath(__file__)) + '/static'
        chdir(static_path)
        self.assertEquals(static_path, file_utils.find_project_dir())
        chdir(BASE_DIR)

    def test_find_project_dir_from_subdir(self):
        static_path = dirname(realpath(__file__)) + '/static'
        chdir(static_path + '/home')
        self.assertEquals(static_path, file_utils.find_project_dir())
        chdir(BASE_DIR)


if __name__ == "__main__":
    unittest.main()
