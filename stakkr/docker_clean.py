#!/usr/bin/env python
"""
Clean unused containers, images, volumes and networks
That saves a lot of space ... should be removed later by "docker ***** prune
"""

import click
import sys

from subprocess import Popen, DEVNULL, PIPE, STDOUT


@click.command(
    help="Clean Docker containers, images, volumes and networks that are not in use",
    name="docker-clean")
@click.option('--force', '-f', help="Do it", is_flag=True)
@click.option('--verbose', '-v', help="Display more information about what is removed", is_flag=True)
def clean(force: bool, verbose: bool):
    click.secho('Clean Docker stopped containers, images, volumes and networks', fg='green')

    remove_containers(force, verbose)
    print()
    remove_images(force, verbose)
    print()
    remove_volumes(force, verbose)
    print()
    remove_networks(force, verbose)

    if force is False:
        click.secho("\n--force is not set so I won't do anything\n", fg='red')

    click.secho('Done', fg='green')


def remove_containers(force: bool, verbose: bool):
    containers = _exec_cmd(['docker', 'ps', '--no-trunc', '-a', '-q', '-f', 'status=exited'])

    if len(containers) == 0:
        print('No exited container to remove')
        return

    print('Removing {} exited container(s)'.format(len(containers)))

    for container in containers:
        _display_entry_info('container', container.decode(), verbose)
        _remove_entry('container', container.decode(), force)



def remove_images(force: bool, verbose: bool):
    images = _exec_cmd(['docker', 'image', 'ls'])

    if len(images) == 0:
        print('No image to remove')
        return

    print('Removing {} image(s)'.format(len(images)))
    if force is True:
        _prune_images()


def remove_networks(force: bool, verbose: bool):
    networks = _exec_cmd(['docker', 'network', 'ls', '--no-trunc', '-q', '--filter', 'type=custom'])

    if len(networks) == 0:
        print('No network to remove')
        return

    print('Removing {} exited networks(s)'.format(len(networks)))

    for network in networks:
        _display_entry_info('network', network.decode(), verbose)
        _remove_entry('network', network.decode(), force)


def remove_volumes(force: bool, verbose: bool):
    volumes = _exec_cmd(['docker', 'volume', 'ls', '-q', '-f', 'dangling=true'])

    if len(volumes) == 0:
        print('No volume to remove')
        return

    print('Removing {} exited volumes(s)'.format(len(volumes)))

    for volume in volumes:
        if verbose is True:
            print('  Removing volume {}'.format(volume.decode()))

        _remove_entry('volume', volume.decode(), force)


def _display_entry_info(entry_type: str, entry: str, verbose: bool):
    if verbose is False:
        return

    base_cmd = ['docker']
    if entry_type != 'container':
        base_cmd += [entry_type]

    info = _exec_cmd(base_cmd + ['inspect', '--format={{.Name}}', entry])[0]
    print('  Removing {} {}'.format(entry_type, info.decode()))


def _exec_cmd(cmd: list):
    return Popen(cmd, stdout=PIPE, stderr=STDOUT).communicate()[0].splitlines()


def _prune_images():
    try:
        _exec_cmd(['docker', 'image', 'prune', '--all', '--force'])
    except Exception as e:
        click.secho('Error removing images', fg='red')


def _remove_entry(entry_type: str, entry: str, force: bool):
    if force is False:
        return

    try:
        base_cmd = ['docker']
        if entry_type != 'container':
            base_cmd += [entry_type]
        _exec_cmd(base_cmd + ['rm', entry])
    except Exception as e:
        output = e.output.decode()
        click.secho('Error removing a {}: {}'.format(entry_type, output), fg='red')


def main():
    try:
        clean()
    except Exception as e:
        msg = click.style(r""" ______ _____  _____   ____  _____
|  ____|  __ \|  __ \ / __ \|  __ \
| |__  | |__) | |__) | |  | | |__) |
|  __| |  _  /|  _  /| |  | |  _  /
| |____| | \ \| | \ \| |__| | | \ \
|______|_|  \_\_|  \_\\____/|_|  \_\

""", fg='yellow')
        msg += click.style('{}'.format(e), fg='red')

        click.echo(msg)
        print()
        # raise e
        sys.exit(1)


if __name__ == '__main__':
    main()
