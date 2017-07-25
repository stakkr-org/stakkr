import os
import sys
import unittest

from click.testing import CliRunner
from stakkr.docker_clean import clean

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


class DockerCleanTest(unittest.TestCase):
    def test_no_arg(self):
        result = CliRunner().invoke(clean)
        self.assertEqual(0, result.exit_code)

        res = result.output
        self.assertRegex(res, 'Clean Docker stopped containers, images, volumes and networks.*')


    def test_bad_arg(self):
        result = CliRunner().invoke(clean, ['hello-world'])
        self.assertEqual(2, result.exit_code)
        self.assertRegex(result.output, 'Usage: docker-clean \[OPTIONS\].*')
