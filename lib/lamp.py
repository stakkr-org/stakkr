import os
import sys
import subprocess

from clint.textui import colored, puts, columns
from lib import docker


class Lamp():
    def __init__(self, base_dir: str):
        self.lamp_base_dir = base_dir
        self.current_dir = os.getcwd()
        # Make sure we are in the right directory
        self.current_dir_relative = self.current_dir[len(self.lamp_base_dir):].lstrip('/')
        os.chdir(self.lamp_base_dir)

        from lib.configreader import Config
        self.default_config_main = Config('conf/compose.ini.tpl').read()['main']
        self.user_config_main = Config('conf/compose.ini').read()['main']
        self.project_name = self.user_config_main.get('project_name')
        self.vms = docker.get_vms(self.project_name)
        self.running_vms = 0
        for vm_id, vm_data in self.vms.items():
            if vm_data['running'] is False:
                continue

            self.running_vms += 1

    def run_services_post_scripts(self):
        if os.name == 'nt':
            puts(colored.red('Could not run service post scripts under Windows'))
            return

        services = [service for service in self.user_config_main.get('services', '').split(',') if service != '']
        for service in services:
            service_script = 'services/' + service + '.sh'
            vm_name = self.get_vm_item(service, 'name')
            if os.path.isfile(service_script) is False:
                continue

            subprocess.call(['bash', service_script, vm_name])


    def display_services_ports(self):
        dns_started = docker.container_running('docker_dns')
        services_to_display = {
            'apache': {'name': 'Web Server', 'url': 'http://{URL}'},
            'mailcatcher': {'name': 'Mailcatcher (fake SMTP)', 'url': 'http://{URL}', 'extra_port': 25},
            'maildev': {'name': 'Maildev (Fake SMTP)', 'url': 'http://{URL}', 'extra_port': 25},
            'mongoclient': {'name': 'MongoDB Client', 'url': 'http://{URL}:3000'},
            'phpmyadmin': {'name': 'PhpMyAdmin', 'url': 'http://{URL}'},
            'xhgui': {'name': 'XHGui (PHP Profiling)', 'url': 'http://{URL}'}
        }

        for service, options in sorted(services_to_display.items()):
            ip = self.get_vm_item(service, 'ip')
            if ip == '':
                continue
            url = options['url'].replace('{URL}', self.get_vm_item(service, 'ip'))

            if dns_started is True:
                url = options['url'].replace('{URL}', '{}.docker'.format(self.get_vm_item(service, 'name')))

            puts('  - For {}'.format(colored.yellow(options['name'])).ljust(55, ' ') + ' : ' + url)

            if 'extra_port' in options:
                puts(' '*3 + ' ... and in your VM use the port {}'.format(options['extra_port']))

        print('')


    def start(self, pull: bool, recreate: bool):
        if pull is True:
            subprocess.call(['python', 'bin/compose', 'pull'])

        recreate_param = '--no-recreate'
        if recreate is True:
            recreate_param = '--force-recreate'

        subprocess.call(['python', 'bin/compose', 'up', '-d', recreate_param, '--remove-orphans'])
        self.vms = docker.get_vms(self.project_name)
        self.run_services_post_scripts()


    def stop(self):
        self.check_vms_are_running()
        subprocess.call(['python', 'bin/compose', 'stop'])


    def restart(self, pull: bool, recreate: bool):
        self.stop()
        self.start(pull, recreate)


    def status(self):
        self.check_vms_are_running()

        dns_started = docker.container_running('docker_dns')

        puts(columns(
            [(colored.green('VM')), 16],
            [(colored.green('HostName' if dns_started else 'IP')), 38],
            [(colored.green('Ports')), 25],
            [(colored.green('Image')), 25],
            [(colored.green('Docker ID')), 15],
            [(colored.green('Docker Name')), 25]
        ))
        puts(columns(
            ['-'*16, 16],
            ['-'*38, 38],
            ['-'*25, 25],
            ['-'*25, 25],
            ['-'*15, 15],
            ['-'*25, 25]
        ))
        for vm_id, vm_data in self.vms.items():
            if vm_data['ip'] == '':
                continue

            puts(columns(
                [vm_data['compose_name'], 16],
                ['{}.docker'.format(vm_data['name']) if dns_started else vm_data['ip'], 38],
                [', '.join(vm_data['ports']), 25],
                [vm_data['image'], 25],
                [vm_id[:12], 15],
                [vm_data['name'], 25]
            ))


    def fullstart(self):
        subprocess.call(['python', 'bin/compose', 'build'])
        self.start()


    def console(self, vm: str, user: str):
        self.check_vms_are_running()

        vm_name = self.get_vm_item(vm, 'name')
        if vm_name == '':
            raise Exception('{} does not seem to be in your services or has crashed'.format(vm))

        tty = 't' if sys.stdin.isatty() else ''
        subprocess.call(['docker', 'exec', '-u', user, '-i' + tty, vm_name, 'env', 'TERM=xterm', 'bash'])


    def run_php(self, user: str, args: str):
        self.check_vms_are_running()

        tty = 't' if sys.stdin.isatty() else ''
        cmd = ['docker', 'exec', '-u', user, '-i' + tty, self.get_vm_item('php', 'name'), 'bash', '-c', '--']
        cmd += ['cd /var/' + self.current_dir_relative + '; exec /usr/bin/php ' + args]
        subprocess.call(cmd, stdin=sys.stdin)


    def run_mysql(self, args: str):
        self.check_vms_are_running()

        vm_name = self.get_vm_item('mysql', 'name')
        if vm_name == '':
            raise Exception('mysql does not seem to be in your services or has crashed')

        tty = 't' if sys.stdin.isatty() else ''
        password = self.user_config_main.get(
            'mysql.root_password',
            self.default_config_main.get('mysql.root_password')
        )
        cmd = ['docker', 'exec', '-u', 'root', '-i' + tty, vm_name]
        cmd += ['mysql', '-u', 'root', '-p' + password, args]
        subprocess.call(cmd, stdin=sys.stdin)


    def manage_dns(self, action: str):
        dns_started = docker.container_running('docker_dns')
        if (dns_started is True and action == 'start') or (dns_started is False and action == 'stop'):
            puts(colored.red("Can't {} the dns container as (already done?)".format(action, action)))
            sys.exit(1)

        if dns_started is True and action == 'stop':
            cmd = ['docker', 'stop', 'docker_dns']
            subprocess.check_output(cmd)
            cmd = ['docker', 'rm', 'docker_dns']
            subprocess.check_output(cmd)
        elif dns_started is False and action == 'start':
            self.docker_run_dns()


    def docker_run_dns(self):
        network = self.project_name + '_lamp'
        try:
            cmd = ['docker', 'run', '-d', '--hostname', 'docker-dns', '--name', 'docker_dns', '--network', network]
            cmd += ['-v', '/var/run/docker.sock:/tmp/docker.sock', '-v', '/etc/resolv.conf:/tmp/resolv.conf']
            cmd += ['mgood/resolvable']
            subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        except Exception as e:
            puts(colored.red("Looks like a dns container is present, deleting it and starting it."))
            subprocess.check_output(['docker', 'rm', 'docker_dns'])
            self.manage_dns('start')
            sys.exit(0)


    def get_vm_item(self, compose_name: str, item_name: str):
        for vm_id, vm_data in self.vms.items():
            if vm_data['compose_name'] == compose_name:
                return vm_data[item_name]

        return ''


    def check_vms_are_running(self):
        if self.running_vms == 0:
            raise Exception('Have you started your server with the start or fullstart action ?')
