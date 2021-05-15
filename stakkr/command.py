# coding: utf-8
"""
Command Wrapper.

A command wrapper to get a live output displayed.
"""

import subprocess
import sys
from click import echo, style


def launch_cmd_displays_output(cmd: list, print_msg: bool = True, print_err: bool = True,
                               err_to_out: bool = False):
    """Launch a command and displays conditionally messages and / or errors."""
    try:
        stderr = subprocess.PIPE if err_to_out is False else subprocess.STDOUT
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=stderr)
    except Exception as error:
        raise SystemError('Cannot run the command: {}'.format(error))

    _read_messages(result, print_msg)
    if print_err is True and err_to_out is False:
        _print_errors(result)

    return result


def verbose(display: bool, message: str):
    """Display a message if verbose is On."""
    if display is True:
        echo(style('[VERBOSE]', fg='green') +
             ' {}'.format(message), file=sys.stderr)


def _read_messages(result: subprocess.Popen, display: bool = False):
    """Print messages sent to the STDOUT."""
    for line in result.stdout:
        line = line.decode()
        line = line if display is True else '.'
        sys.stdout.write(line)

    sys.stdout.write("\n")


def _print_errors(result: subprocess.Popen):
    """Print messages sent to the STDERR."""
    num = 0
    for line in result.stderr:
        err = line.decode()

        if num == 0:
            sys.stdout.write(style("Command returned errors :", fg='red'))

        if num < 5:
            sys.stdout.write(err)
        elif num == 5:
            sys.stdout.write(style('... and more', fg='red'))

        num += 1

    sys.stdout.write("\n")
