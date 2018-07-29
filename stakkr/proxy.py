"""
Manage public proxy to expose containers
"""

import os
from stakkr import docker_actions
from stakkr.configreader import Config


class Proxy():
    """Main class that does actions asked in the cli"""

    def __init__(self, port: int = 80, proxy_name: str = 'stakkr_proxy'):
        """Set the right values to start the proxy"""

        self.port = port
        self.proxy_name = proxy_name

    def start(self, stakkr_network: str):
        """Start stakkr proxy if stopped"""

        if container_running[self.proxy_name] is True:
            return

        api_client = docker_actions.get_api_client()
        # Start the CT

        # Connect it to the main network
        docker_actions.add_container_to_network(self.proxy_name, stakkr_network)

    def stop(self):
        """Stop stakkr proxy"""

        if container_running[self.proxy_name] is False:
            return
