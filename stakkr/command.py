"""
A command wrapper to get a live output displayed. Useful when you need to write a plugin that outputs some progress
bar or info.
"""

import subprocess
import sys

from click import style
from io import BufferedReader


def launch_cmd_displays_output(cmd: list, print_msg=True, print_err=True, err_to_out=False):
    """Launch a command and displays conditionnaly messages and / or errors"""

    try:
        stderr = subprocess.PIPE if err_to_out is False else subprocess.STDOUT
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=stderr)
    except Exception as e:
        raise SystemError('Cannot run the command: {}'.format(e))

    _read_messages(result, print_msg)
    if print_err is True and err_to_out is False:
        _print_errors(result)

    return result


def _read_messages(result: BufferedReader, display: bool = False):
    """Print messages sent to the STDOUT"""

    for line in result.stdout:
        line = line.decode()
        line = line if display is True else '.'
        print(line, end='')
        sys.stdout.flush()

    print()


def _print_errors(result: BufferedReader):
    """Print messages sent to the STDERR"""

    i = 0
    for line in result.stderr:
        err = line.decode()

        if i == 0:
            print(style("Command returned errors :", fg='red'))

        if i < 5:
            print(err, end='')
        elif i is 5:
            print(style('... and more', fg='red'))

        i += 1
