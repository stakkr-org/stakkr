import os
import sys
import subprocess

from clint.textui import colored, puts
from io import BufferedReader


def launch_cmd_displays_output(cmd: list, displays_messages=True, displays_errors=True):
    try:
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        puts(colored.red("Can't run the command : {}".format(e.output.decode() if e.output else "... unknown")))
        sys.exit(1)

    if displays_messages is True:
        print_messages(result)
    if displays_errors is True:
        print_errors(result)

    return result


def print_messages(result: BufferedReader):
    for line in result.stdout:
        print(line.decode(), end='')


def print_errors(result: BufferedReader):
    i = 0
    for line in result.stderr:
        if i == 0:
            puts(colored.red("Can't run the command, it returned:"))

        print(line.decode(), end='')


        if i > 5:
            puts(colored.red('... and more'))
            break

        i += 1
