#!/usr/bin/env python
"""
Clean unused containers, images, volumes and networks
That saves a lot of space ... should be removed later by "docker ***** prune
"""

import sys
from subprocess import check_output, CalledProcessError, STDOUT
import click


@click.command(help="""Clean Docker containers, images, volumes and networks
that are not in use""", name="docker-clean")
@click.option('--force', '-f', help="Do it", is_flag=True)
@click.option('--verbose', '-v', help="Display more information about what is removed",
              is_flag=True)
def clean(force: bool, verbose: bool):
    """See command help"""

    click.secho('Clean Docker stopped containers, images, volumes and networks', fg='green')

    remove_containers(force, verbose)
    remove_images(force)
    remove_volumes(force, verbose)
    remove_networks(force, verbose)

    if force is False:
        click.secho("\n--force is not set so I won't do anything", fg='red')


def remove_containers(force: bool, verbose: bool):
    """Remove exited containers"""

    res = _exec_cmd(['docker', 'ps', '--no-trunc', '-a', '-q', '-f', 'status=exited'])
    containers = res.splitlines()
    if len(containers) is 0:
        print('- No exited container to remove')
        return

    click.echo('- Removing {} exited container(s)'.format(len(containers)))

    for container in containers:
        _display_entry_info('container', container.decode(), verbose)
        _remove_entry('container', container.decode(), force)


def remove_images(force: bool):
    """Prune all images"""

    res = _exec_cmd(['docker', 'image', 'ls'])
    images = res.splitlines()
    if len(images) is 1:
        click.echo('- No image to remove')
        return

    click.echo('- Removing {} image(s)'.format(len(images) - 1))
    if force is True:
        _prune_images()


def remove_networks(force: bool, verbose: bool):
    """Remove custom networks (not systems)"""

    res = _exec_cmd(['docker', 'network', 'ls', '--no-trunc', '-q', '--filter', 'type=custom'])
    networks = res.splitlines()
    if len(networks) is 0:
        click.echo('- No network to remove')
        return

    click.echo('- Removing {} exited networks(s)'.format(len(networks)))

    for network in networks:
        _display_entry_info('network', network.decode(), verbose)
        _remove_entry('network', network.decode(), force)


def remove_volumes(force: bool, verbose: bool):
    """Remove dangling volumes"""

    res = _exec_cmd(['docker', 'volume', 'ls', '-q', '-f', 'dangling=true'])
    volumes = res.splitlines()
    if len(volumes) is 0:
        click.echo('- No volume to remove')
        return

    click.echo('- Removing {} exited volumes(s)'.format(len(volumes)))

    for volume in volumes:
        if verbose is True:
            click.echo('  Removing volume {}'.format(volume.decode()))

        _remove_entry('volume', volume.decode(), force)


def _display_entry_info(entry_type: str, entry: str, verbose: bool):
    if verbose is False:
        return

    base_cmd = ['docker'] if entry_type == 'container' else ['docker', entry_type]
    res = _exec_cmd(base_cmd + ['inspect', '--format={{.Name}}', entry])
    info = res.splitlines()[0]
    click.echo('  Removing {} {}'.format(entry_type, info.decode()))


def _exec_cmd(cmd: list):
    try:
        return check_output(cmd, stderr=STDOUT)
    except CalledProcessError:
        click.secho('  Error running command : "{}"'.format(' '.join(cmd)), fg='red')


def _prune_images():
    _exec_cmd(['docker', 'image', 'prune', '--all', '--force'])


def _remove_entry(entry_type: str, entry: str, force: bool):
    if force is False:
        return

    base_cmd = ['docker'] if entry_type == 'container' else ['docker', entry_type]
    _exec_cmd(base_cmd + ['rm', entry])


def main():
    """Main function when the CLI Script is called directly"""

    try:
        clean()
    except Exception as error:
        msg = click.style(r""" ______ _____  _____   ____  _____
|  ____|  __ \|  __ \ / __ \|  __ \
| |__  | |__) | |__) | |  | | |__) |
|  __| |  _  /|  _  /| |  | |  _  /
| |____| | \ \| | \ \| |__| | | \ \
|______|_|  \_\_|  \_\\____/|_|  \_\

""", fg='yellow')
        msg += click.style('{}'.format(error), fg='red')

        click.echo(msg)
        click.echo()
        # raise error
        sys.exit(1)


if __name__ == '__main__':
    main()
