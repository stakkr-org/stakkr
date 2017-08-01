import os
import sys
import subprocess

from clint.textui import colored, puts, columns
from . import command
from . import docker
from .configreader import Config


class StakkrActions():
    """Main class that does actions asked in the cli"""

    def __init__(self, base_dir: str, ctx: dict):
        # Work with directories and move to the right place
        self.stakkr_base_dir = base_dir
        self.context = ctx
        self.current_dir = os.getcwd()
        self.current_dir_relative = self._get_relative_dir()
        os.chdir(self.stakkr_base_dir)

        # Set some general variables
        self.dns_container_name = 'docker_dns'
        self.config_file = ctx['CONFIG']
        self.compose_base_cmd = self._get_compose_base_cmd()

        # Get info from config
        self.user_config_main = self._get_config()
        self.project_name = self.user_config_main.get('project_name')


    def console(self, ct: str, user: str):
        """Enter a container (stakkr allows only apache / php and mysql)"""

        docker.check_cts_are_running(self.project_name, self.config_file)

        ct_name = docker.get_ct_name(ct)
        tty = 't' if sys.stdin.isatty() else ''
        subprocess.call(['docker', 'exec', '-u', user, '-i' + tty, ct_name, 'env', 'TERM=xterm', 'bash'])


    def display_services_ports(self):
        """Once started, stakkr displays a message with the list of launched containers."""

        services_to_display = {
            'apache': {'name': 'Web Server', 'url': 'http://{}'},
            'mailcatcher': {'name': 'Mailcatcher (fake SMTP)', 'url': 'http://{}', 'extra_port': 25},
            'maildev': {'name': 'Maildev (Fake SMTP)', 'url': 'http://{}', 'extra_port': 25},
            'phpmyadmin': {'name': 'PhpMyAdmin', 'url': 'http://{}'},
            'xhgui': {'name': 'XHGui (PHP Profiling)', 'url': 'http://{}'}
        }

        dns_started = docker.container_running('docker_dns')
        print('To access your services:')
        for service, options in sorted(services_to_display.items()):
            ip = docker.get_ct_item(service, 'ip')
            if ip == '':
                continue

            url = self._get_url(options['url'], service, dns_started)
            puts('  - For {}'.format(colored.yellow(options['name'])).ljust(55, ' ') + ' : ' + url)

            if 'extra_port' in options:
                puts(' '*3 + ' ... in your containers use the port {}'.format(options['extra_port']))
                print()


    def exec(self, container: str, user: str, args: tuple):
        """Run a command from outside to any container. Wrapped into /bin/sh"""

        docker.check_cts_are_running(self.project_name, self.config_file)

        args = ['"{}"'.format(arg) for arg in args]

        tty = 't' if sys.stdin.isatty() else ''
        cmd = ['docker', 'exec', '-u', user, '-i' + tty, docker.get_ct_name(container), 'sh', '-c']
        cmd += ["""test -d "/var/{0}" && cd "/var/{0}" ; exec {1}""".format(self.current_dir_relative, ' '.join(args))]
        self._verbose('Command : "' + ' '.join(cmd) + '"')
        subprocess.call(cmd, stdin=sys.stdin)


    def manage_dns(self, action: str):
        """Starts or stop the DNS forwarder"""

        dns_started = docker.container_running(self.dns_container_name)

        if dns_started is True and action == 'stop':
            cmd = ['docker', 'stop', 'docker_dns']
            command.launch_cmd_displays_output(cmd, self.context['VERBOSE'], self.context['DEBUG'])
            return
        elif dns_started is False and action == 'start':
            self._docker_run_dns()
            return

        puts(colored.red('[ERROR]') + " Can't {} the dns container (already done?)".format(action))
        sys.exit(1)


    def start(self, pull: bool, recreate: bool):
        """If not started, start the containers defined in config"""

        verb = self.context['VERBOSE']
        debug = self.context['DEBUG']

        try:
            docker.check_cts_are_running(self.project_name, self.config_file)
            puts(colored.yellow('[INFO]') + ' stakkr is already started ...')
            sys.exit(0)
        except Exception:
            pass

        if pull is True:
            command.launch_cmd_displays_output(self.compose_base_cmd + ['pull'], verb, debug, True)

        recreate_param = '--force-recreate' if recreate is True else '--no-recreate'
        cmd = self.compose_base_cmd + ['up', '-d', recreate_param, '--remove-orphans']
        self._verbose('Command: ' + ' '.join(cmd))
        command.launch_cmd_displays_output(cmd, verb, debug, True)

        self.running_cts, self.cts = docker.get_running_containers(self.project_name, self.config_file)
        if self.running_cts is 0:
            raise SystemError("Couldn't start the containers, run the start with '-v' and '-d'")

        self._run_services_post_scripts()


    def status(self):
        """Returns a nice table with the list of started containers"""

        try:
            self.running_cts, self.cts = docker.check_cts_are_running(self.project_name, self.config_file)
        except Exception:
            puts(colored.yellow('[INFO]') + ' stakkr is currently stopped')
            sys.exit(0)

        dns_started = docker.container_running('docker_dns')

        self._print_status_headers(dns_started)
        self._print_status_body(dns_started)


    def stop(self):
        """If started, stop the containers defined in config. Else throw an error"""

        verb = self.context['VERBOSE']
        debug = self.context['DEBUG']

        docker.check_cts_are_running(self.project_name, self.config_file)
        command.launch_cmd_displays_output(self.compose_base_cmd + ['stop'], verb, debug, True)

        self.running_cts, self.cts = docker.get_running_containers(self.project_name, self.config_file)
        if self.running_cts is not 0:
            raise SystemError("Couldn't stop services ...")


    def _call_service_post_script(self, service: str):
        service_script = 'services/' + service + '.sh'
        if os.path.isfile(service_script) is True:
            subprocess.call(['bash', service_script, docker.get_ct_item(service, 'name')])


    def _docker_run_dns(self):
        docker.check_cts_are_running(self.project_name, self.config_file)

        try:
            cmd = ['docker', 'run', '--rm', '-d', '--hostname', 'docker-dns', '--name', self.dns_container_name]
            cmd += ['--network', self.project_name + '_stakkr']
            cmd += ['-v', '/var/run/docker.sock:/tmp/docker.sock', '-v', '/etc/resolv.conf:/tmp/resolv.conf']
            cmd += ['mgood/resolvable']
            command.launch_cmd_displays_output(cmd, self.context['VERBOSE'], self.context['DEBUG'])
        except Exception as e:
            puts(colored.red('[ERROR]') + " Can't start the DNS, maybe it exists already ?")
            sys.exit(1)


    def _get_compose_base_cmd(self):
        if self.context['CONFIG'] is None:
            return ['stakkr-compose']

        return ['stakkr-compose', '-c', self.context['CONFIG']]


    def _get_config(self):
        config = Config(self.config_file)
        user_config_main = config.read()
        if user_config_main is False:
            config.display_errors()
            sys.exit(1)

        return user_config_main['main']


    def _get_relative_dir(self):
        if self.current_dir.startswith(self.stakkr_base_dir):
            return self.current_dir[len(self.stakkr_base_dir):].lstrip('/')

        return ''


    def _get_url(self, service_url: str, service: str, dns_started: bool):
        name = docker.get_ct_name(service) if dns_started else docker.get_ct_item(service, 'ip')

        return service_url.format(name)


    def _print_status_headers(self, dns_started: bool):
        host_ip = (colored.green('HostName' if dns_started else 'IP'))

        puts(columns(
            [(colored.green('Container')), 16], [host_ip, 25], [(colored.green('Ports')), 25],
            [(colored.green('Image')), 32],
            [(colored.green('Docker ID')), 15], [(colored.green('Docker Name')), 25]
            ))

        puts(columns(
            ['-'*16, 16], ['-'*25, 25], ['-'*25, 25],
            ['-'*32, 32],
            ['-'*15, 15], ['-'*25, 25]
            ))


    def _print_status_body(self, dns_started: bool):
        for ct_id, ct_data in self.cts.items():
            if ct_data['ip'] == '':
                continue

            host_ip = ct_data['name'] if dns_started else ct_data['ip']

            puts(columns(
                [ct_data['compose_name'], 16], [host_ip, 25], [', '.join(ct_data['ports']), 25],
                [ct_data['image'], 32],
                [ct_id[:12], 15], [ct_data['name'], 25]
                ))


    def _run_services_post_scripts(self):
        """A service can have a .sh file that will be executed once it's started.
        Useful to override some actions of the classical /run.sh

        """

        if os.name == 'nt':
            puts(colored.red('Could not run service post scripts under Windows'))
            return

        for service in self.user_config_main.get('services'):
            self._call_service_post_script(service)


    def _verbose(self, message: str):
        if self.context['VERBOSE'] is True:
            print(colored.green('[VERBOSE]') + ' {}'.format(message))
