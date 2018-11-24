#!/usr/bin/env python
# coding: utf-8
"""
Docker Clean command.

Clean unused containers, images, volumes and networks.
That saves a lot of space ...
"""

import sys
from subprocess import check_output, CalledProcessError, STDOUT
import click
import humanfriendly
from stakkr.docker_actions import get_client as get_docker_client


@click.command(help="""Clean Docker containers, images, volumes and networks
that are not in use""", name="docker-clean")
@click.option('--force', '-f', help="Do it", is_flag=True)
@click.option('--containers/--no-containers', '-c/', help="Remove containers", is_flag=True, default=True)
@click.option('--images/--no-images', '-i/', help="Remove images", is_flag=True, default=True)
@click.option('--volumes/--no-volumes', '-V/', help="Remove volumes", is_flag=True, default=True)
@click.option('--networks/--no-networks', '-n/', help="Remove networks", is_flag=True, default=True)
def clean(force: bool, containers: bool, images: bool, volumes: bool, networks: bool):
    """See command help."""
    if containers is True:
        click.secho('Cleaning Docker stopped containers:', fg='green')
        remove_containers(force)
    if images is True:
        click.secho('Cleaning Docker unused images:', fg='green')
        remove_images(force)
    if volumes is True:
        click.secho('Cleaning Docker unused volumes:', fg='green')
        remove_volumes(force)
    if networks is True:
        click.secho('Cleaning Docker unused networks:', fg='green')
        remove_networks(force)


def remove_containers(force: bool):
    """Remove exited containers."""
    stopped_containers = get_docker_client().containers.list(filters={'status': 'exited'})
    if len(stopped_containers) is 0:
        print('  No exited container to remove')
        return

    if force is False:
        click.secho("  --force is not set so I won't do anything", fg='red')
        return

    res = get_docker_client().containers.prune()
    cts = len(res['ContainersDeleted'])
    space = humanfriendly.format_size(res['SpaceReclaimed'])
    click.echo('  Removed {} exited container(s), saved {}'.format(cts, space))


def remove_images(force: bool):
    """Remove unused images."""
    if force is False:
        click.secho("  --force is not set so I won't do anything", fg='red')
        return

    res = get_docker_client().images.prune(filters={'dangling': False})
    if res['ImagesDeleted'] is None:
        print('  No image to remove')
        return

    images = len(res['ImagesDeleted'])
    space = humanfriendly.format_size(res['SpaceReclaimed'])
    click.echo('  Removed {} images(s), saved {}'.format(images, space))


def remove_networks(force: bool):
    """Remove unused networks."""
    if force is False:
        click.secho("  --force is not set so I won't do anything", fg='red')
        return

    res = get_docker_client().networks.prune()
    if res['NetworksDeleted'] is None:
        print('  No network to remove')
        return

    networks = len(res['NetworksDeleted'])
    click.echo('  Removed {} network(s)'.format(networks))


def remove_volumes(force: bool):
    """Remove unused volumes."""
    if force is False:
        click.secho("  --force is not set so I won't do anything", fg='red')
        return

    res = get_docker_client().volumes.prune()
    if res['VolumesDeleted'] is None or len(res['VolumesDeleted']) is 0:
        print('  No volume to remove')
        return

    volumes = len(res['VolumesDeleted'])
    space = humanfriendly.format_size(res['SpaceReclaimed'])
    click.echo('  Removed {} volume(s), saved {}'.format(volumes, space))


def main():
    """Generate the CLI."""
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
