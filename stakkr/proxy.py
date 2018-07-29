"""
Manage public proxy to expose containers
"""

import os
from stakkr import docker_actions
from stakkr.configreader import Config


class Proxy():
    """Main class that does actions asked in the cli"""

    proxy_name = 'stakkr_proxy'


    def __init__(self, port: int):
        pass


    def start(self, connect_network: str):
        if container_running[self.proxy_name] is False:
            return

        api_client = docker_actions.get_api_client()

        docker_actions.add_container_to_network(self.proxy_name, connect_network)


    def stop(self):
        pass
