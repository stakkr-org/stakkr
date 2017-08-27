"""
Manage DNS Start / Stop by creating the container or attaching to the
current stakkr network
"""

import sys
import click
from docker.errors import DockerException
from stakkr import docker_actions
CT_NAME = 'docker_dns'


def manage_dns(project_name: str, action: str):
    """Control the start or stop of DNS forwarder"""

    dns_started = docker_actions.container_running(CT_NAME)
    if dns_started is True and action == 'stop':
        dns = docker_actions.get_client().containers.get('docker_dns')
        return dns.stop()

    elif action == 'start':
        run_dns(project_name)
        return

    click.echo(click.style('[ERROR]', fg='red') + " DNS already stopped")
    sys.exit(1)


def run_dns(project_name: str):
    """Either add the DNS to the network if started or start it"""

    network = project_name + '_stakkr'

    # Started ? Only attach it to the current network
    if docker_actions.container_running(CT_NAME) is True:
        docker_actions.add_container_to_network(CT_NAME, network)
        return

    # Not started ? Create it and add it to the network
    try:
        volumes = ['/var/run/docker.sock:/tmp/docker.sock', '/etc/resolv.conf:/tmp/resolv.conf']
        docker_actions.get_client().containers.run(
            'mgood/resolvable', remove=True, detach=True, network=network,
            hostname='docker-dns', name=CT_NAME, volumes=volumes)
    except DockerException as error:
        click.echo(click.style('[ERROR]', fg='red') + " Can't start the DNS ...")
        click.echo('Error was -> {}'.format(error))
        sys.exit(1)
