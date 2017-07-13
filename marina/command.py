"""
A command wrapper to get a live output displayed. Useful when you need to write a plugin that outputs some progress
bar or info.
"""


import sys
import subprocess

from clint.textui import colored, puts
from io import BufferedReader


def launch_cmd_displays_output(cmd: list, displays_messages=True, displays_errors=True):
    """Launch a command and displays conditionnaly messages and / or errors"""

    try:
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        puts(colored.red("Can't run the command : {}".format(e.output.decode() if e.output else "... unknown")))
        sys.exit(1)

    if displays_messages is True:
        _print_messages(result)
    if displays_errors is True:
        _print_errors(result)

    return result


def _print_messages(result: BufferedReader):
    """Print messages sent to the STDOUT"""

    for line in result.stdout:
        print(line.decode(), end='')


def _print_errors(result: BufferedReader):
    """Print messages sent to the STDERR"""

    i = 0
    for line in result.stderr:
        if i == 0:
            puts(colored.red("Can't run the command, it returned:"))

        print(line.decode(), end='')


        if i > 5:
            puts(colored.red('... and more'))
            break

        i += 1
