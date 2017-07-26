import io
import os
import re
import sys
import unittest

from contextlib import redirect_stdout
from stakkr.command import launch_cmd_displays_output

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


# https://docs.python.org/3/library/unittest.html#assert-methods
class CommandTest(unittest.TestCase):
    cmd_ok = ['echo', 'coucou']
    cmd_nook = ['cat', '/does/not/exist']
    cmd_err = ['echoo']

    def test_command_without_stdout_ok(self):
        f = io.StringIO()
        with redirect_stdout(f):
            launch_cmd_displays_output(self.cmd_ok, False, False)
        res = f.getvalue()
        self.assertEqual('.', res[:1])

        try:
            from contextlib import redirect_stderr
        except Exception:
            return

        f = io.StringIO()
        with redirect_stderr(f):
            launch_cmd_displays_output(self.cmd_ok, False, False)
        res = f.getvalue()
        self.assertEqual('', res)


    def test_command_with_stdout_ok(self):
        f = io.StringIO()
        with redirect_stdout(f):
            launch_cmd_displays_output(self.cmd_ok, True, False)
        res = f.getvalue()
        self.assertEqual('coucou\n\n', res)

        try:
            from contextlib import redirect_stderr
        except Exception:
            return

        f = io.StringIO()
        with redirect_stderr(f):
            launch_cmd_displays_output(self.cmd_ok, True, False)
        res = f.getvalue()
        self.assertEqual('', res)


    def test_command_with_stderr_no_stdout_ok(self):
        f = io.StringIO()
        with redirect_stdout(f):
            launch_cmd_displays_output(self.cmd_ok, False, True)
        res = f.getvalue()
        self.assertEqual('.', res[:1])

        try:
            from contextlib import redirect_stderr
        except Exception:
            return

        f = io.StringIO()
        with redirect_stderr(f):
            launch_cmd_displays_output(self.cmd_ok, False, True)
        res = f.getvalue()
        self.assertEqual('', res)


    def test_command_exception(self):
        with self.assertRaisesRegex(SystemError, "Cannot run the command: \[Errno 2\] No such file or directory: 'echoo'"):
            launch_cmd_displays_output(self.cmd_err, True, True)


    def test_command_without_stderr_and_stdout_err(self):
        f = io.StringIO()
        with redirect_stdout(f):
            launch_cmd_displays_output(self.cmd_nook, False, False)
        res = f.getvalue()
        self.assertEqual('\n', res)

        try:
            from contextlib import redirect_stderr
        except Exception:
            return

        f = io.StringIO()
        with redirect_stderr(f):
            launch_cmd_displays_output(self.cmd_nook, False, False)
        res = f.getvalue()
        self.assertEqual('', res)


    def test_command_without_stderr_but_stdout_err(self):
        f = io.StringIO()
        with redirect_stdout(f):
            launch_cmd_displays_output(self.cmd_nook, True, False)
        res = f.getvalue()
        self.assertEqual('\n', res)

        try:
            from contextlib import redirect_stderr
        except Exception:
            return

        f = io.StringIO()
        with redirect_stderr(f):
            launch_cmd_displays_output(self.cmd_nook, True, False)
        res = f.getvalue()
        self.assertEqual('', res)


    def test_command_with_stderr_no_stdout_err(self):
        f = io.StringIO()
        with redirect_stdout(f):
            launch_cmd_displays_output(self.cmd_nook, False, True)
        res = f.getvalue()
        expected = re.compile('.*No such file or directory.*', re.MULTILINE)
        self.assertRegex(res, expected)

        try:
            from contextlib import redirect_stderr
        except Exception:
            return

        f = io.StringIO()
        with redirect_stderr(f):
            launch_cmd_displays_output(self.cmd_nook, False, True)
        res = f.getvalue()
        self.assertEqual('', res)


    def test_command_with_stderr_no_stdout_err_loop(self):
        f = io.StringIO()
        with redirect_stdout(f):
            launch_cmd_displays_output(['wget', '--debug', '--tries', '3', 'http://doesnotexist'], False, True)
        res = f.getvalue()
        expected = re.compile('.*\.\.\. and more.*', re.MULTILINE)
        self.assertRegex(res, expected)

        try:
            from contextlib import redirect_stderr
        except Exception:
            return

        f = io.StringIO()
        with redirect_stderr(f):
            launch_cmd_displays_output(self.cmd_nook, False, True)
        res = f.getvalue()
        self.assertEqual('', res)



if __name__ == "__main__":
    unittest.main()
