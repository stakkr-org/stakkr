# coding: utf-8
"""Manage public proxy to expose containers."""

import click
from sys import stdout
from docker.errors import DockerException
from stakkr import docker_actions as docker
from stakkr.file_utils import get_dir


class Proxy:
    """Main class that does actions asked by the cli."""

    def __init__(self,
                 http_port: int = 80, https_port: int = 443,
                 ct_name: str = 'proxy_stakkr',
                 version: str = 'latest'):
        """Set the right values to start the proxy."""

        self.ports = {'http': http_port, 'https': https_port}
        self.ct_name = ct_name
        self.docker_client = docker.get_client()
        self.version = version

    def start(self, stakkr_network: str = None):
        """Start stakkr proxy if stopped."""
        if docker.container_running(self.ct_name) is False:
            msg = ' traefik (Dashboard: http://traefik.docker.localhost)\n'
            stdout.write(click.style('[STARTING]', fg='green') + msg)
            self._start_container()

        # Connect it to network if asked
        if stakkr_network is not None:
            docker.add_container_to_network(self.ct_name, stakkr_network)

    def stop(self):
        """Stop stakkr proxy."""
        if docker.container_running(self.ct_name) is False:
            return

        stdout.write(click.style('[STOPPING]', fg='green') + ' traefik\n')
        proxy_ct = self.docker_client.containers.get(self.ct_name)
        proxy_ct.stop()

    def _start_container(self):
        """Start proxy."""
        proxy_conf_dir = get_dir('static/proxy')
        try:
            self.docker_client.images.pull('traefik:{}'.format(self.version))
            self.docker_client.containers.run(
                'traefik:{}'.format(self.version), remove=True, detach=True,
                hostname=self.ct_name, name=self.ct_name,
                volumes=[
                    '/var/run/docker.sock:/var/run/docker.sock:ro',
                    '{}/traefik.yml:/etc/traefik/traefik.yml:ro'.format(proxy_conf_dir),
                    '{}/config.yml:/etc/traefik/config.yml'.format(proxy_conf_dir),
                    '{}/ssl:/etc/traefik/ssl'.format(proxy_conf_dir)],
                labels={'traefik.enable': 'true', 'traefik.http.routers.traefik': 'true'},
                ports={80: self.ports['http'], 443: self.ports['https']}
                )
        except DockerException as error:
            raise RuntimeError("Can't start proxy ...({})".format(error))
