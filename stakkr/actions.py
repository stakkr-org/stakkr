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
        self.stakkr_base_dir = base_dir
        self.context = ctx
        self.current_dir = os.getcwd()

        # Make sure we are in the right directory
        self.current_dir_relative = self.current_dir[len(self.stakkr_base_dir):].lstrip('/')
        os.chdir(self.stakkr_base_dir)

        self.dns_container_name = 'docker_dns'
        self.config_file = ctx['CONFIG']
        self.compose_base_cmd = ['stakkr-compose'] if ctx['CONFIG'] is None else ['stakkr-compose', '-c', ctx['CONFIG']]

        self.user_config_main = self._get_config()
        self.project_name = self.user_config_main.get('project_name')
        self.running_cts = self._get_num_running_containers()


    def check_cts_are_running(self):
        """Throws an error if cts are not running"""

        if not self.running_cts:
            raise SystemError('Have you started your server with the start or fullstart action ?')


    def console(self, ct: str, user: str):
        """Enter a container (stakkr allows only apache / php and mysql)"""

        self.check_cts_are_running()

        ct_name = self.get_ct_item(ct, 'name')
        if ct_name == '':
            raise Exception('{} does not seem to be in your services or has crashed'.format(ct))

        tty = 't' if sys.stdin.isatty() else ''
        subprocess.call(['docker', 'exec', '-u', user, '-i' + tty, ct_name, 'env', 'TERM=xterm', 'bash'])


    def display_services_ports(self):
        """Once started, stakkr displays a message with the list of launched containers."""

        services_to_display = {
            'apache': {'name': 'Web Server', 'url': 'http://{URL}'},
            'mailcatcher': {'name': 'Mailcatcher (fake SMTP)', 'url': 'http://{URL}', 'extra_port': 25},
            'maildev': {'name': 'Maildev (Fake SMTP)', 'url': 'http://{URL}', 'extra_port': 25},
            'phpmyadmin': {'name': 'PhpMyAdmin', 'url': 'http://{URL}'},
            'xhgui': {'name': 'XHGui (PHP Profiling)', 'url': 'http://{URL}'}
        }

        dns_started = docker.container_running('docker_dns')
        print()
        for service, options in sorted(services_to_display.items()):
            ip = self.get_ct_item(service, 'ip')
            if ip == '':
                continue

            url = self._get_url(options['url'], service, dns_started)
            puts('  - For {}'.format(colored.yellow(options['name'])).ljust(55, ' ') + ' : ' + url)

            if 'extra_port' in options:
                puts(' '*3 + ' ... in your containers use the port {}'.format(options['extra_port']))
        print()


    def get_ct_item(self, compose_name: str, item_name: str):
        """Get a value frrom a container, such as name or IP"""

        for ct_id, ct_data in self.cts.items():
            if ct_data['compose_name'] == compose_name:
                return ct_data[item_name]

        return ''


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


    def restart(self, pull: bool, recreate: bool):
        """Restart (smartly) the containers defined in config : stop=start and start=stop+start"""

        if self.running_cts:
            self.stop()

        self.start(pull, recreate)


    def run_mysql(self, args: str):
        """Run a MySQL command from outside. Useful to import an SQL File."""

        self.check_cts_are_running()

        ct_name = self.get_ct_item('mysql', 'name')
        if ct_name == '':
            raise Exception('mysql does not seem to be in your services or has crashed')

        tty = 't' if sys.stdin.isatty() else ''
        password = self.user_config_main.get('mysql.root_password')
        cmd = ['docker', 'exec', '-u', 'root', '-i' + tty, ct_name]
        cmd += ['mysql', '-u', 'root', '-p' + password, args]
        subprocess.call(cmd, stdin=sys.stdin)


    def run_php(self, user: str, args: str):
        """Run a script or PHP command from outside"""

        self.check_cts_are_running()

        tty = 't' if sys.stdin.isatty() else ''
        cmd = ['docker', 'exec', '-u', user, '-i' + tty, self.get_ct_item('php', 'name'), 'bash', '-c', '--']
        cmd += ['cd /var/' + self.current_dir_relative + '; exec /usr/bin/php ' + args]
        subprocess.call(cmd, stdin=sys.stdin)


    def start(self, pull: bool, recreate: bool):
        """If not started, start the containers defined in config"""

        verb = self.context['VERBOSE']
        debug = self.context['DEBUG']

        if self.running_cts:
            puts(colored.yellow('[INFO]') + ' stakkr is already started ...')
            sys.exit(0)

        if pull is True:
            command.launch_cmd_displays_output(self.compose_base_cmd + ['pull'], verb, debug)

        recreate_param = '--force-recreate' if recreate is True else '--no-recreate'
        cmd = self.compose_base_cmd + ['up', '-d', recreate_param, '--remove-orphans']
        command.launch_cmd_displays_output(cmd, verb, debug)

        self.running_cts = self._get_num_running_containers()
        if self.running_cts is 0:
            raise SystemError("Couldn't start the containers, run the start with '-v' and '-d'")

        self._run_services_post_scripts()


    def status(self):
        """Returns a nice table with the list of started containers"""

        if not self.running_cts:
            puts(colored.yellow('[INFO]') + ' stakkr is currently stopped')
            sys.exit(0)

        dns_started = docker.container_running('docker_dns')

        puts(columns(
            [(colored.green('Container')), 16],
            [(colored.green('HostName' if dns_started else 'IP')), 25],
            [(colored.green('Ports')), 25],
            [(colored.green('Image')), 32],
            [(colored.green('Docker ID')), 15],
            [(colored.green('Docker Name')), 25]
        ))
        puts(columns(
            ['-'*16, 16],
            ['-'*25, 25],
            ['-'*25, 25],
            ['-'*32, 32],
            ['-'*15, 15],
            ['-'*25, 25]
        ))
        for ct_id, ct_data in self.cts.items():
            if ct_data['ip'] == '':
                continue

            puts(columns(
                [ct_data['compose_name'], 16],
                [ct_data['name'] if dns_started else ct_data['ip'], 25],
                [', '.join(ct_data['ports']), 25],
                [ct_data['image'], 32],
                [ct_id[:12], 15],
                [ct_data['name'], 25]
            ))


    def stop(self):
        """If started, stop the containers defined in config. Else throw an error"""

        self.check_cts_are_running()
        command.launch_cmd_displays_output(self.compose_base_cmd + ['stop'], self.context['VERBOSE'], self.context['DEBUG'])

        self.running_cts = self._get_num_running_containers()
        if self.running_cts is not 0:
            raise SystemError("Couldn't stop services ...")


    def _call_service_post_script(self, service: str):
        service_script = 'services/' + service + '.sh'
        ct_name = self.get_ct_item(service, 'name')
        if os.path.isfile(service_script) is False:
            return

        subprocess.call(['bash', service_script, ct_name])


    def _docker_run_dns(self):
        """Starts the DNS"""

        self.check_cts_are_running()

        try:
            cmd = ['docker', 'run', '--rm', '-d', '--hostname', 'docker-dns', '--name', self.dns_container_name]
            cmd += ['--network', self.project_name + '_stakkr']
            cmd += ['-v', '/var/run/docker.sock:/tmp/docker.sock', '-v', '/etc/resolv.conf:/tmp/resolv.conf']
            cmd += ['mgood/resolvable']
            command.launch_cmd_displays_output(cmd, self.context['VERBOSE'], self.context['DEBUG'])
        except Exception as e:
            puts(colored.red('[ERROR]') + " Can't start the DNS, maybe it exists already ?")
            sys.exit(1)


    def _get_config(self):
        config = Config(self.config_file)
        user_config_main = config.read()
        if user_config_main is False:
            config.display_errors()
            sys.exit(1)

        return user_config_main['main']


    def _get_num_running_containers(self):
        self.cts = docker.get_running_containers(self.project_name, self.config_file)

        return sum(True for ct_id, ct_data in self.cts.items() if ct_data['running'] is True)


    def _get_url(self, service_url: str, service: str, dns_started: bool):
        url = service_url.replace('{URL}', self.get_ct_item(service, 'ip'))

        if dns_started is True:
            url = service_url.replace('{URL}', '{}'.format(self.get_ct_item(service, 'name')))

        return url


    def _run_services_post_scripts(self):
        """
        A service can have a .sh file that will be executed once it's started.
        Useful to override some actions of the classical /run.sh
        """

        if os.name == 'nt':
            puts(colored.red('Could not run service post scripts under Windows'))
            return

        for service in self.user_config_main.get('services'):
            self._call_service_post_script(service)
