"""
Patch OS when required. For example, allow access to subnet for Windows
and later for Mac (TBD)
"""

import os
import subprocess
from click import echo, secho
from stakkr import docker_actions


def start(project_name: str):
    """For Windows we need to do a few manipulations to be able to access
    our dev environment from the host ...

    Found here: https://github.com/docker/for-win/issues/221#issuecomment-270576243"""

    if os.name not in ['nt']:
        return

    docker_actions.get_client().containers.run(
        'justincormack/nsenter1', remove=True, tty=True, privileged=True, network_mode='none',
        pid_mode='host', command='bin/sh -c "iptables -A FORWARD -j ACCEPT"')

    subnet = docker_actions.get_subnet(project_name)
    switch_ip = docker_actions.get_switch_ip()
    msg = 'We need to create a route for the network {} via {} to work...'
    secho(msg.format(subnet, switch_ip), fg='yellow', nl=False)
    subprocess.call(['route', 'add', subnet, 'MASK', '255.255.255.0', switch_ip])
    echo()


def stop(project_name: str):
    """Opposite actions than start() : cleanup"""

    if os.name not in ['nt']:
        return

    subnet = docker_actions.get_subnet(project_name)
    msg = "Let's remove the route that has been added for {}...".format(subnet)
    secho(msg, fg='yellow', nl=False)
    subprocess.call(['route', 'delete', subnet])
    echo()
