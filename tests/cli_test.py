import os
import sys
import unittest

from click.testing import CliRunner
from stakkr.cli import stakkr

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


class CliTest(unittest.TestCase):
    def test_no_arg(self):
        result = CliRunner().invoke(stakkr)
        self.assertEqual(0, result.exit_code)
        self.assertEqual('Usage: stakkr [OPTIONS] COMMAND [ARGS]', result.output[:38])


    def test_bad_arg(self):
        result = CliRunner().invoke(stakkr, ['hello-world'])
        self.assertEqual(2, result.exit_code)
        self.assertEqual('Usage: stakkr [OPTIONS] COMMAND [ARGS]', result.output[:38])

        res_out = result.output[-38:].strip()
        self.assertEqual('Error: No such command "hello-world".', res_out)


    def test_stop_not_started(self):
        args = ['-c', base_dir + '/static/config_valid.ini', 'stop']
        with self.assertRaisesRegex(SystemError, 'Have you started your server with the start or fullstart action.*'):
            result = CliRunner().invoke(cli=stakkr, args=args, obj={}, catch_exceptions=False)
            self.assertIs(1, result.exit_code)


    def test_status_not_started(self):
        args = ['-c', base_dir + '/static/config_valid.ini', 'status']
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli=stakkr, args=args, obj={}, catch_exceptions=False)
            self.assertEqual('[INFO] stakkr is currently stopped', result.output.strip())
            self.assertIs(0, result.exit_code)
