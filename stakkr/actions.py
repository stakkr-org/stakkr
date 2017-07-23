import os
import sys
import subprocess

from clint.textui import colored, puts, columns
from click.core import Context
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

        # self.default_config_main = Config('conf/compose.ini.tpl').read()['main']
        config = Config()
        user_config_main = config.read()
        if user_config_main is False:
            config.display_errors()
            sys.exit(1)

        self.user_config_main = user_config_main['main']
        self.project_name = self.user_config_main.get('project_name')
        self.vms = docker.get_running_containers(self.project_name)
        self.running_vms = sum(True for vm_id, vm_data in self.vms.items() if vm_data['running'] is True)


    def display_services_ports(self):
        """Once started, stakkr displays a message with the list of launched containers."""

        dns_started = docker.container_running('docker_dns')
        services_to_display = {
            'apache': {'name': 'Web Server', 'url': 'http://{URL}'},
            'mailcatcher': {'name': 'Mailcatcher (fake SMTP)', 'url': 'http://{URL}', 'extra_port': 25},
            'maildev': {'name': 'Maildev (Fake SMTP)', 'url': 'http://{URL}', 'extra_port': 25},
            'phpmyadmin': {'name': 'PhpMyAdmin', 'url': 'http://{URL}'},
            'xhgui': {'name': 'XHGui (PHP Profiling)', 'url': 'http://{URL}'}
        }

        for service, options in sorted(services_to_display.items()):
            ip = self.get_vm_item(service, 'ip')
            if ip == '':
                continue
            url = options['url'].replace('{URL}', self.get_vm_item(service, 'ip'))

            if dns_started is True:
                url = options['url'].replace('{URL}', '{}'.format(self.get_vm_item(service, 'name')))

            puts('  - For {}'.format(colored.yellow(options['name'])).ljust(55, ' ') + ' : ' + url)

            if 'extra_port' in options:
                puts(' '*3 + ' ... and in your VM use the port {}'.format(options['extra_port']))

        print('')


    def start(self, pull: bool, recreate: bool):
        """If not started, start the containers defined in config"""

        if self.running_vms:
            puts(colored.yellow("stakkr is already started ..."))
            sys.exit(0)

        if pull is True:
            subprocess.call(['stakkr-compose', 'pull'])

        recreate_param = '--force-recreate' if recreate is True else '--no-recreate'
        cmd = ['stakkr-compose', 'up', '-d', recreate_param, '--remove-orphans']
        command.launch_cmd_displays_output(cmd, self.context['VERBOSE'], self.context['DEBUG'])
        self.vms = docker.get_running_containers(self.project_name)
        self._run_services_post_scripts()


    def stop(self):
        """If started, stop the containers defined in config. Else throw an error"""

        self.check_vms_are_running()
        command.launch_cmd_displays_output(['stakkr-compose', 'stop'], self.context['VERBOSE'], self.context['DEBUG'])
        self.running_vms = 0


    def restart(self, pull: bool, recreate: bool):
        """Restart (smartly) the containers defined in config : stop=start and start=stop+start"""

        if self.running_vms:
            self.stop()

        self.start(pull, recreate)


    def status(self):
        """Returns a nice table with the list of started containers"""

        if not self.running_vms:
            puts(colored.yellow("stakkr is currently stopped"))
            sys.exit(0)

        dns_started = docker.container_running('docker_dns')

        puts(columns(
            [(colored.green('VM')), 16],
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
        for vm_id, vm_data in self.vms.items():
            if vm_data['ip'] == '':
                continue

            puts(columns(
                [vm_data['compose_name'], 16],
                [vm_data['name'] if dns_started else vm_data['ip'], 25],
                [', '.join(vm_data['ports']), 25],
                [vm_data['image'], 32],
                [vm_id[:12], 15],
                [vm_data['name'], 25]
            ))


    def fullstart(self):
        """Build the image dynamically if git repos are given for a service"""

        subprocess.call(['stakkr-compose', 'build'])
        self.start()


    def console(self, vm: str, user: str):
        """Enter a container (stakkr allows only apache / php and mysql)"""

        self.check_vms_are_running()

        vm_name = self.get_vm_item(vm, 'name')
        if vm_name == '':
            raise Exception('{} does not seem to be in your services or has crashed'.format(vm))

        tty = 't' if sys.stdin.isatty() else ''
        subprocess.call(['docker', 'exec', '-u', user, '-i' + tty, vm_name, 'env', 'TERM=xterm', 'bash'])


    def run_php(self, user: str, args: str):
        """Run a script or PHP command from outside"""

        self.check_vms_are_running()

        tty = 't' if sys.stdin.isatty() else ''
        cmd = ['docker', 'exec', '-u', user, '-i' + tty, self.get_vm_item('php', 'name'), 'bash', '-c', '--']
        cmd += ['cd /var/' + self.current_dir_relative + '; exec /usr/bin/php ' + args]
        subprocess.call(cmd, stdin=sys.stdin)


    def run_mysql(self, args: str):
        """Run a MySQL command from outside. Useful to import an SQL File."""

        self.check_vms_are_running()

        vm_name = self.get_vm_item('mysql', 'name')
        if vm_name == '':
            raise Exception('mysql does not seem to be in your services or has crashed')

        tty = 't' if sys.stdin.isatty() else ''
        password = self.user_config_main.get('mysql.root_password')
        cmd = ['docker', 'exec', '-u', 'root', '-i' + tty, vm_name]
        cmd += ['mysql', '-u', 'root', '-p' + password, args]
        subprocess.call(cmd, stdin=sys.stdin)


    def manage_dns(self, action: str):
        """Starts or stop the DNS forwarder"""

        dns_started = docker.container_running(self.dns_container_name)

        if dns_started is True and action == 'stop':
            cmd = ['docker', 'stop', 'docker_dns']
            subprocess.check_output(cmd)
            return
        elif dns_started is False and action == 'start':
            self._docker_run_dns()
            return

        puts(colored.red("Can't {} the dns container as (already done?)".format(action)))
        sys.exit(1)


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


    def _call_service_post_script(self, service: str):
        service_script = 'services/' + service + '.sh'
        vm_name = self.get_vm_item(service, 'name')
        if os.path.isfile(service_script) is False:
            return

        subprocess.call(['bash', service_script, vm_name])


    def _docker_run_dns(self):
        """Starts the DNS"""

        self.check_vms_are_running()

        try:
            docker.create_network('dns')
            cmd = ['docker', 'run', '--rm', '-d', '--hostname', 'docker-dns', '--name', self.dns_container_name]
            cmd += ['--network', self.project_name + '_stakkr']
            cmd += ['-v', '/var/run/docker.sock:/tmp/docker.sock', '-v', '/etc/resolv.conf:/tmp/resolv.conf']
            cmd += ['mgood/resolvable']
            subprocess.check_output(cmd)
        except Exception as e:
            puts(colored.red("Can't start the DNS, maybe it exists already ?"))
            sys.exit(1)


    def get_vm_item(self, compose_name: str, item_name: str):
        """Get a value frrom a VM, such as name or IP"""

        for vm_id, vm_data in self.vms.items():
            if vm_data['compose_name'] == compose_name:
                return vm_data[item_name]

        return ''


    def check_vms_are_running(self):
        """Throws an error if vms are not running"""

        if not self.running_vms:
            raise Exception('Have you started your server with the start or fullstart action ?')
