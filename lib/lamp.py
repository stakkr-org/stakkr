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

        self.vms = docker.get_vms()

        self.running_vms = 0
        for vm_id, vm_data in self.vms.items():
            if vm_data['running'] is False:
                continue

            self.running_vms += 1


    def run_services_post_scripts(self):
        services = [service for service in self.user_config_main.get('services', '').split(',') if service != '']
        for service in services:
            service_script = 'services/' + service + '.sh'
            vm_name = self.get_vm_item(service, 'name')
            if os.path.isfile(service_script) is False:
                continue

            subprocess.call(['bash', service_script, vm_name])


    def display_services_ports(self):
        dns_started = docker.container_running('docker_dns')

        apache_url = '{}.docker'.format(self.get_vm_item('apache', 'name')) if dns_started is True else self.get_vm_item('apache', 'ip')
        puts('{} URL : http://{}'.format(colored.yellow('Web server'), apache_url))

        if self.get_vm_item('mailcatcher', 'ip') != '':
            mailcatcher_ip = '{}.docker'.format(self.get_vm_item('mailcatcher', 'name')) if dns_started is True else self.get_vm_item('mailcatcher', 'ip')
            puts('For {} use : http://{}'.format(colored.yellow('mailcatcher'), mailcatcher_ip))
            puts(' '*16 + 'and in your VM use the server "{}" with the port 25\n'.format(colored.yellow('mailcatcher')))

        if self.get_vm_item('maildev', 'ip') != '':
            maildev_ip = '{}.docker'.format(self.get_vm_item('maildev', 'name')) if dns_started is True else self.get_vm_item('maildev', 'ip')
            puts('For {} use : http://{}'.format(colored.yellow('maildev'), maildev_ip))
            puts(' '*12 + 'and in your VM use the server "{}" with the port 25\n'.format(colored.yellow('maildev')))

        if self.get_vm_item('mongoclient', 'ip') != '':
            mongoclient_ip = '{}.docker'.format(self.get_vm_item('mongoclient', 'name')) if dns_started is True else self.get_vm_item('mongoclient', 'ip')
            puts('For {} use : http://{}:3000\n'.format(colored.yellow('mongoclient'), mongoclient_ip))

        if self.get_vm_item('phpmyadmin', 'ip') != '':
            pma_ip = '{}.docker'.format(self.get_vm_item('phpmyadmin', 'name')) if dns_started is True else self.get_vm_item('phpmyadmin', 'ip')
            puts('For {} use : http://{}\n'.format(colored.yellow('phpMyAdmin'), pma_ip))

        if self.get_vm_item('xhgui', 'ip') != '':
            xhgui_ip = '{}.docker'.format(self.get_vm_item('xhgui', 'name')) if dns_started is True else self.get_vm_item('xhgui', 'ip')
            puts('For {} use : http://{}\n'.format(colored.yellow('xhgui'), xhgui_ip))


    def start(self, pull: bool, recreate: bool):
        if pull is True:
            subprocess.call(['bin/compose', 'pull'])

        recreate_param = '--no-recreate'
        if recreate is True:
            recreate_param = '--force-recreate'

        subprocess.call(['bin/compose', 'up', '-d', recreate_param, '--remove-orphans'])
        self.vms = docker.get_vms()
        self.run_services_post_scripts()


    def stop(self):
        self.check_vms_are_running()
        subprocess.call(['bin/compose', 'stop'])


    def restart(self, pull: bool, recreate: bool):
        self.stop()
        self.start(pull, recreate)


    def status(self):
        self.check_vms_are_running()
        puts(columns(
            [(colored.green('VM')), 20],
            [(colored.green('IP')), 15],
            [(colored.green('Ports')), 30],
            [(colored.green('Image')), 30],
            [(colored.green('Docker ID')), 15],
            [(colored.green('Docker Name')), 25]
        ))
        puts(columns(
            ['-'*20, 20],
            ['-'*15, 15],
            ['-'*30, 30],
            ['-'*30, 30],
            ['-'*15, 15],
            ['-'*25, 25]
        ))
        for vm_id, vm_data in self.vms.items():
            if vm_data['ip'] == '':
                continue

            puts(columns(
                [vm_data['compose_name'], 20],
                [vm_data['ip'], 15],
                [', '.join(vm_data['ports']), 30],
                [vm_data['image'], 30],
                [vm_id[:12], 15],
                [vm_data['name'], 25]
            ))


    def fullstart(self):
        subprocess.call(['bin/compose', 'build'])
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
        if dns_started is True and action == 'start':
            puts(colored.red("Can't start the dns container as it's already started"))
            sys.exit(1)
        elif dns_started is False and action == 'stop':
            puts(colored.red("Can't stop the dns container as it's not running"))
            sys.exit(1)
        elif dns_started is True and action == 'stop':
            cmd = ['docker', 'stop', 'docker_dns']
            subprocess.call(cmd)
            cmd = ['docker', 'rm', 'docker_dns']
            subprocess.check_output(cmd)
        elif dns_started is False and action == 'start':
            cmd = ['docker', 'run', '-d', '--hostname', 'docker-dns', '--name', 'docker_dns']
            cmd += ['-v', '/var/run/docker.sock:/tmp/docker.sock', '-v', '/etc/resolv.conf:/tmp/resolv.conf']
            cmd += ['mgood/resolvable']
            subprocess.check_output(cmd)


    def get_vm_item(self, compose_name: str, item_name: str):
        for vm_id, vm_data in self.vms.items():
            if vm_data['compose_name'] == compose_name:
                return vm_data[item_name]

        return ''


    def check_vms_are_running(self):
        if self.running_vms == 0:
            raise Exception('Have you started your server with the start or fullstart action ?')
