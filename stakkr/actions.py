# coding: utf-8
"""Stakkr main controller. Used by the CLI to do all its actions."""

import os
from platform import system as os_name
import subprocess
import sys
import click
from clint.textui import colored, puts, columns
from stakkr import command, docker_actions as docker
from stakkr.configreader import Config
from stakkr.proxy import Proxy


class StakkrActions:
    """Main class that does actions asked in the cli."""

    def __init__(self, ctx: dict):
        """Set all require properties."""
        self.context = ctx

        # Set some general variables
        self.config = None
        self.project_name = None
        self.project_dir = None
        self.cwd_relative = None

    def console(self, container: str, user: str, tty: bool):
        """Enter a container. Stakkr will try to guess the right shell."""
        self.init_project()

        docker.check_cts_are_running(self.project_name)

        tty = 't' if tty is True else ''
        ct_name = docker.get_ct_name(container)
        cmd = ['docker', 'exec', '-u', user, '-i' + tty]
        cmd += [docker.get_ct_name(container), docker.guess_shell(ct_name)]
        subprocess.call(cmd)

        command.verbose(self.context['VERBOSE'], 'Command : "' + ' '.join(cmd) + '"')

    def get_services_urls(self):
        """Once started, displays a message with a list of running containers."""
        self.init_project()

        cts = docker.get_running_containers(self.project_name)[1]

        text = ''
        for _, ct_info in cts.items():
            service_config = self.config['services'][ct_info['compose_name']]
            if ({'service_name', 'service_url'} <= set(service_config)) is False:
                continue

            url = self.get_url(service_config['service_url'], ct_info['compose_name'])
            name = colored.yellow(service_config['service_name'])

            text += '  - For {}'.format(name).ljust(55, ' ') + ' : ' + url + '\n'

            if 'service_extra_ports' in service_config:
                ports = ', '.join(map(str, service_config['service_extra_ports']))
                text += ' '*4 + '(In your containers use the host '
                text += '"{}" and port(s) {})\n'.format(ct_info['compose_name'], ports)

        return text

    def exec_cmd(self, container: str, user: str, args: tuple, tty: bool):
        """Run a command from outside to any container. Wrapped into /bin/sh."""
        self.init_project()

        docker.check_cts_are_running(self.project_name)

        # Protect args to avoid strange behavior in exec
        args = ['"{}"'.format(arg) for arg in args]

        tty = 't' if tty is True else ''
        ct_name = docker.get_ct_name(container)
        cmd = ['docker', 'exec', '-u', user, '-i' + tty, ct_name, 'sh', '-c']
        cmd += ["""test -d "/var/{0}" && cd "/var/{0}" ; exec {1}""".format(self.cwd_relative, ' '.join(args))]
        command.verbose(self.context['VERBOSE'], 'Command : "' + ' '.join(cmd) + '"')
        subprocess.call(cmd, stdin=sys.stdin)

    def get_config(self):
        """Read and validate config from config file"""
        config = Config(self.context['CONFIG'])
        main_config = config.read()
        if main_config is False:
            config.display_errors()
            sys.exit(1)

        return main_config

    def init_project(self):
        """
        Initializing the project by reading config and
        setting some properties of the object
        """
        if self.config is not None:
            return

        self.config = self.get_config()
        self.project_name = self.config['project_name']
        self.project_dir = self.config['project_dir']
        sys.path.append(self.project_dir)

        self.cwd_relative = self._get_relative_dir()
        os.chdir(self.project_dir)

    def start(self, container: str, pull: bool, recreate: bool, proxy: bool):
        """If not started, start the containers defined in config."""
        self.init_project()
        verb = self.context['VERBOSE']
        debug = self.context['DEBUG']

        self._is_up(container)

        if pull is True:
            command.launch_cmd_displays_output(self._get_compose_base_cmd() + ['pull'], verb, debug, True)

        recreate_param = '--force-recreate' if recreate is True else '--no-recreate'
        cmd = self._get_compose_base_cmd() + ['up', '-d', recreate_param, '--remove-orphans']
        cmd += _get_single_container_option(container)

        command.verbose(self.context['VERBOSE'], 'Command: ' + ' '.join(cmd))
        command.launch_cmd_displays_output(cmd, verb, debug, True)

        running_cts, cts = docker.get_running_containers(self.project_name)
        if not running_cts:
            raise SystemError("Couldn't start the containers, run the start with '-v' and '-d'")

        self._run_iptables_rules(cts)
        if proxy is True:
            conf = self.config['proxy']
            Proxy(conf.get('http_port'), conf.get('https_port')).start(
                docker.get_network_name(self.project_name))

    def status(self):
        """Return a nice table with the list of started containers."""
        self.init_project()

        try:
            docker.check_cts_are_running(self.project_name)
        except SystemError:
            puts(colored.yellow('[INFO]') + ' stakkr is currently stopped')
            sys.exit(0)

        _, cts = docker.get_running_containers(self.project_name)

        _print_status_headers()
        _print_status_body(cts)

    def stop(self, container: str, proxy: bool):
        """If started, stop the containers defined in config. Else throw an error."""
        self.init_project()
        verb = self.context['VERBOSE']
        debug = self.context['DEBUG']

        docker.check_cts_are_running(self.project_name)

        cmd = self._get_compose_base_cmd() + ['stop'] + _get_single_container_option(container)
        command.launch_cmd_displays_output(cmd, verb, debug, True)

        running_cts, _ = docker.get_running_containers(self.project_name)
        if running_cts and container is None:
            raise SystemError("Couldn't stop services ...")

        if proxy is True:
            Proxy().stop()

    def _get_compose_base_cmd(self):
        if self.context['CONFIG'] is None:
            return ['stakkr-compose']

        return ['stakkr-compose', '-c', self.context['CONFIG']]

    def _get_relative_dir(self):
        if os.getcwd().startswith(self.project_dir):
            return os.getcwd()[len(self.project_dir):].lstrip('/')

        return ''

    def _is_up(self, container: str):
        try:
            docker.check_cts_are_running(self.project_name)
        except SystemError:
            return

        if container is None:
            puts(colored.yellow('[INFO]') + ' stakkr is already started ...')
            sys.exit(0)

        # If single container : check if that specific one is running
        ct_name = docker.get_ct_item(container, 'name')
        if docker.container_running(ct_name):
            puts(colored.yellow('[INFO]') + ' service {} is already started ...'.format(container))
            sys.exit(0)

    def _run_iptables_rules(self, cts: dict):
        """For some containers we need to add iptables rules added from the config."""
        for _, ct_info in cts.items():
            container = ct_info['compose_name']
            ct_config = self.config['services'][container]
            if 'blocked_ports' not in ct_config:
                continue

            blocked_ports = ct_config['blocked_ports']
            error, msg = docker.block_ct_ports(container, blocked_ports, self.project_name)
            if error is True:
                click.secho(msg, fg='red')
                continue

            command.verbose(self.context['VERBOSE'], msg)

    def get_url(self, service_url: str, service: str):
        """Build URL to be displayed."""
        proxy_conf = self.config['proxy']
        # By default our URL is the IP
        url = docker.get_ct_item(service, 'ip')
        # If proxy enabled, display nice urls
        if bool(proxy_conf['enabled']):
            http_port = int(proxy_conf['http_port'])
            url = docker.get_ct_item(service, 'traefik_host').lower()
            url += '' if http_port == 80 else ':{}'.format(http_port)
        elif os_name() in ['Windows', 'Darwin']:
            puts(colored.yellow('[WARNING]') + ' Under Win and Mac, you need the proxy enabled')

        return service_url.format(url)


def _get_single_container_option(container: str):
    if container is None:
        return []

    return [container]


def _print_status_headers():
    """Display messages for stakkr status (header)"""
    puts(columns(
        [(colored.green('Container')), 16], [colored.green('IP'), 15],
        [(colored.green('Url')), 32], [(colored.green('Image')), 32],
        [(colored.green('Docker ID')), 15], [(colored.green('Docker Name')), 25]
    ))

    puts(columns(
        ['-'*16, 16], ['-'*15, 15],
        ['-'*32, 32], ['-'*32, 32],
        ['-'*15, 15], ['-'*25, 25]
    ))


def _print_status_body(cts: dict):
    """Display messages for stakkr status (body)"""
    for container in sorted(cts.keys()):
        ct_data = cts[container]
        if ct_data['ip'] == '':
            continue

        puts(columns(
            [ct_data['compose_name'], 16], [ct_data['ip'], 15],
            [ct_data['traefik_host'], 32], [ct_data['image'], 32],
            [ct_data['id'][:12], 15], [ct_data['name'], 25]
        ))
