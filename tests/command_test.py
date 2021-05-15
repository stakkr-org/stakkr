import os
import re
import sys
import pytest
import unittest
from stakkr.command import launch_cmd_displays_output

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


# https://docs.python.org/3/library/unittest.html#assert-methods
class CommandTest(unittest.TestCase):
    cmd_ok = ['echo', 'coucou']
    cmd_nook = ['cat', '/does/not/exist']
    cmd_err = ['echoo']

    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd

    def test_command_without_stdout_ok(self):
        # TODO make it work under windows
        if os.name == 'nt':
            return

        launch_cmd_displays_output(self.cmd_ok, False, False)
        
        out, err = self.capfd.readouterr()
        self.assertEqual('.', out[:1])
        self.assertEqual('', err)

    def test_command_with_stdout_ok(self):
        # TODO make it work under windows
        if os.name == 'nt':
            return

        launch_cmd_displays_output(self.cmd_ok, True, False)

        out, err = self.capfd.readouterr()
        self.assertEqual('coucou\n\n', out)
        self.assertEqual('', err)

    def test_command_with_stderr_no_stdout_ok(self):
        # TODO make it work under windows
        if os.name == 'nt':
            return

        launch_cmd_displays_output(self.cmd_ok, False, True)

        out, err = self.capfd.readouterr()
        self.assertEqual('.', out[:1])
        self.assertEqual('', err)

    def test_command_exception(self):
        with self.assertRaisesRegex(SystemError, r"Cannot run the command: \[.*Err.*2\]"):
            launch_cmd_displays_output(self.cmd_err, True, True)

    def test_command_without_stderr_and_stdout_err(self):
        # TODO make it work under windows
        if os.name == 'nt':
            return

        launch_cmd_displays_output(self.cmd_nook, False, False)

        out, err = self.capfd.readouterr()
        self.assertEqual('\n', out)
        self.assertEqual('', err)

    def test_command_without_stderr_but_stdout_err(self):
        # TODO make it work under windows
        if os.name == 'nt':
            return

        launch_cmd_displays_output(self.cmd_nook, True, False)

        out, err = self.capfd.readouterr()
        self.assertEqual('\n', out)
        self.assertEqual('', err)

    def test_command_with_stderr_no_stdout_err(self):
        # TODO make it work under windows
        if os.name == 'nt':
            return

        launch_cmd_displays_output(self.cmd_nook, False, True)

        out, err = self.capfd.readouterr()
        expected = re.compile('.*No such file or directory.*', re.MULTILINE)
        self.assertRegex(out, expected)
        self.assertEqual('', err)

    def test_command_with_stderr_no_stdout_err_loop(self):
        # TODO make it work under windows
        if os.name == 'nt':
            return

        cmd = ['cat', 'w', 'r', 'o', 'n', 'g', 'f', 'i', 'l', 'e']
        launch_cmd_displays_output(cmd, False, True)

        out, err = self.capfd.readouterr()
        expected = re.compile(r'.*\.\.\. and more.*', re.MULTILINE)
        self.assertRegex(out, expected)
        self.assertEqual('', err)


if __name__ == "__main__":
    unittest.main()
