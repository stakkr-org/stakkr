# coding: utf-8
"""Manage public proxy to expose containers."""

import click
from docker.errors import DockerException
from stakkr import docker_actions as docker


class Proxy:
    """Main class that does actions asked by the cli."""

    def __init__(self, port: int = 80, proxy_name: str = 'proxy_stakkr'):
        """Set the right values to start the proxy."""
        self.port = port
        self.proxy_name = proxy_name
        self.docker_client = docker.get_client()

    def start(self, stakkr_network: str = None):
        """Start stakkr proxy if stopped."""
        if docker.container_running(self.proxy_name) is False:
            print(click.style('[STARTING]', fg='green') + ' traefik')
            self._start_container()

        # Connect it to network if asked
        if stakkr_network is not None:
            docker.add_container_to_network(self.proxy_name, stakkr_network)

    def stop(self):
        """Stop stakkr proxy."""
        if docker.container_running(self.proxy_name) is False:
            return

        print(click.style('[STOPPING]', fg='green') + ' traefik')
        proxy_ct = self.docker_client.containers.get(self.proxy_name)
        proxy_ct.stop()

    def _start_container(self):
        """Start proxy."""
        try:
            self.docker_client.images.pull('traefik:latest')
            self.docker_client.containers.run(
                'traefik:latest', remove=True, detach=True,
                hostname=self.proxy_name, name=self.proxy_name,
                volumes=['/var/run/docker.sock:/var/run/docker.sock'],
                ports={80: self.port, 8080: 8080}, command='--api --docker')
        except DockerException as error:
            raise RuntimeError("Can't start proxy ...({})".format(error))
