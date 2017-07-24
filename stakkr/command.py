"""
A command wrapper to get a live output displayed. Useful when you need to write a plugin that outputs some progress
bar or info.
"""


import subprocess

from click import style
from io import BufferedReader


def launch_cmd_displays_output(cmd: list, displays_messages=True, displays_errors=True):
    """Launch a command and displays conditionnaly messages and / or errors"""

    try:
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        raise SystemError('Cannot run the command: {}'.format(e))

    _read_messages(result, displays_messages)
    if displays_errors is True:
        _print_errors(result)

    return result


def _read_messages(result: BufferedReader, display: bool = False):
    """Print messages sent to the STDOUT"""

    for line in result.stdout:
        line.decode() if display is False else print(line.decode(), end='')


def _print_errors(result: BufferedReader):
    """Print messages sent to the STDERR"""

    i = 0
    for line in result.stderr:
        if i == 0:
            print(style("Command returned an error :", fg='red'))

        print(line.decode(), end='')

        if i > 5:
            print(style('... and more', fg='red'))
            break

        i += 1
