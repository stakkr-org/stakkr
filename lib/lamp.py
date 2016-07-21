import os
import sys
import subprocess

from argparse import ArgumentParser
from clint.textui import colored, puts, columns
from lib import docker
from lib import sugarcli
from lib import utils


class Lamp():
    def __init__(self, base_dir: str):
        self.lamp_base_dir = base_dir
        self.current_dir = os.getcwd()
        # Make sure we are in the right directory
        self.current_dir_relative = self.current_dir[len(self.lamp_base_dir):].lstrip('/')
        os.chdir(self.lamp_base_dir)

        from lib import configreader
        config_reader = configreader.Config('conf/compose.ini')
        self.config = config_reader.read()

        self.valid_actions = ('start', 'fullstart', 'stop', 'restart', 'status', 'console', 'run-php', 'run-mysql', 'sugarcli', 'sugar-install')
        self.arg_parser = ArgumentParser(description="Process the only argument expected (The action)", usage="./lamp {action}")
        self.arg_parser.add_argument('action', choices=self.valid_actions)

        self.vms = docker.get_vms()

        self.running_vms = 0
        for vm_id, vm_data in self.vms.items():
            if vm_data['running'] is False:
                continue

            self.running_vms += 1


    def run_services_post_scripts(self):
        services = [service for service in self.config['main'].get('services', '').split(',') if service != '']
        for service in services:
            service_script = 'service/' + service + '.sh'
            vm_name = self.__get_vm_item(service, 'name')
            if os.path.isfile(service_script) is False:
                continue

            subprocess.call(['bash', service_script, vm_name])


    def display_services_ports(self):
        puts('To access the {} use : http://{}\n'.format(colored.yellow('web server'), self.__get_vm_item('apache', 'ip')))

        mailcatcher_ip = self.__get_vm_item('mailcatcher', 'ip')
        if mailcatcher_ip != '':
            puts('For {} use : http://{}'.format(colored.yellow('mailcatcher'), mailcatcher_ip))
            puts(' '*16 + 'and in your VM use the server "{}" with the port 25\n'.format(colored.yellow('mailcatcher')))

        maildev_ip = self.__get_vm_item('maildev', 'ip')
        if maildev_ip != '':
            puts('For {} use : http://{}'.format(colored.yellow('maildev'), maildev_ip))
            puts(' '*12 + 'and in your VM use the server "{}" with the port 25\n'.format(colored.yellow('maildev')))

        mongoclient_ip = self.__get_vm_item('mongoclient', 'ip')
        if mongoclient_ip != '':
            puts('For {} use : http://{}:3000\n'.format(colored.yellow('mongoclient'), mongoclient_ip))

        pma_ip = self.__get_vm_item('phpmyadmin', 'ip')
        if pma_ip != '':
            puts('For {} use : http://{}\n'.format(colored.yellow('phpMyAdmin'), pma_ip))


    def start(self):
        subprocess.call(['bin/compose', 'up'])
        self.vms = docker.get_vms()
        self.run_services_post_scripts()


    def stop(self):
        self.__check_vms_are_running()
        subprocess.call(['bin/compose', 'stop'])


    def restart(self):
        self.stop()
        self.start()


    def status(self):
        self.__check_vms_are_running()
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
        self.__check_vms_are_running()

        vm_name = self.__get_vm_item(vm, 'name')
        if vm_name == '':
            raise Exception('{} does not seem to be in your services or has crashed'.format(vm))

        tty = 't' if sys.stdin.isatty() else ''
        subprocess.call(['docker', 'exec', '-u', user, '-i' + tty, vm_name, 'bash'])


    def run_php(self, user: str, args: str):
        self.__check_vms_are_running()

        tty = 't' if sys.stdin.isatty() else ''
        cmd = ['docker', 'exec', '-u', user, '-i' + tty, self.__get_vm_item('php', 'name'), 'bash', '-c', '--']
        cmd += ['cd /var/' + self.current_dir_relative + '; exec /usr/bin/php ' + args]
        subprocess.call(cmd, stdin=sys.stdin)


    def run_mysql(self, args: str):
        self.__check_vms_are_running()

        vm_name = self.__get_vm_item('mysql', 'name')
        if vm_name == '':
            raise Exception('mysql does not seem to be in your services or has crashed')

        tty = 't' if sys.stdin.isatty() else ''
        password = self.config['main'].get('mysql.root_password', 'changeme')
        cmd = ['docker', 'exec', '-u', 'root', '-i' + tty, vm_name]
        cmd += ['mysql', '-u', 'root', '-p' + password, args]
        subprocess.call(cmd, stdin=sys.stdin)


    def sugarcli(self, args: str):
        self.__check_vms_are_running()

        if self.current_dir.find(self.lamp_base_dir) != 0:
            raise Exception('You are not in a sub-directory of your lamp instance')

        sugarcli.run(self.__get_vm_item('php', 'name'), self.current_dir_relative, args)


    def sugar_install(self, sugar_type: str, version: str, path: str, demo_data: bool, force: bool):
        self.__check_vms_are_running()

        if self.current_dir != self.lamp_base_dir:
            raise IOError('That command should be run from the root ({})'.format(self.lamp_base_dir))

        folder_name = path.lstrip('www/')

        if os.path.isdir(path) and force is False:
            raise IOError("Can't install your SugarCRM to {}, folder exists".format(path))

        # Creating the config File, downloading and installing
        password = utils.generate_password()
        config_file = self.__create_and_modify_sugarcrm_config(folder_name, password, demo_data)

        token = self.config['main'].get('pydio.token', None)
        private = self.config['main'].get('pydio.private', None)
        error_message = False
        try:
            sugar_zip_file = sugarcli.download_sugar_package(token, private, sugar_type, version)
            sugarcli.run(
                self.__get_vm_item('php', 'name'),
                self.current_dir_relative,
                'install:run --source {} --config {} --path {} --force'.format(sugar_zip_file, config_file, path))
            os.remove(sugar_zip_file)
        except Exception as e:
            error_message = str(e)

        # the file has been created for sure so delete in all cases
        os.remove(config_file)

        if error_message is not False:
            raise Exception(error_message)

        sugar_url = 'http://' + self.__get_vm_item('apache', 'ip') + '/' + folder_name
        puts('SugarCRM has been installed into ' + colored.green(path))
        puts('Login to ' + colored.green(sugar_url) + ' with ' + colored.green('admin') + ' and ' + colored.red(password))


    def __create_and_modify_sugarcrm_config(self, folder_name: str, password: str, demo_data: bool):
        import uuid
        tmp_config = 'www/config-{}.php'.format(uuid.uuid4())
        install_demo_data = 'yes' if demo_data is True else 'no'

        sugarcli.run(self.__get_vm_item('php', 'name'), self.current_dir_relative, 'install:config:get -c ' + tmp_config)
        if os.path.isfile(tmp_config) is False:
            raise IOError("Config file has not been created by sugarcli")

        import fileinput
        config_file = fileinput.input(tmp_config, inplace=1)
        for line in config_file:
            line = line.replace('<DB_USER>', 'root')
            line = line.replace('<DB_PASSWORD>', self.config['main'].get('mysql.root_password', 'changeme'))
            line = line.replace('<DB_NAME>', 'sugar_' + folder_name.replace('/', '_'))
            line = line.replace("['setup_db_host_name'] = 'localhost';", "['setup_db_host_name'] = 'mysql';")
            line = line.replace("['setup_fts_host'] = 'localhost';", "['setup_fts_host'] = 'elasticsearch';")
            line = line.replace('<SITE_URL>', 'http://' + self.__get_vm_item('apache', 'ip') + '/' + folder_name)
            line = line.replace('<SUGAR_ADMIN_USER>', 'admin')
            line = line.replace('<SUGAR_ADMIN_PASSWORD>', password)
            # line = line.replace('<SUGAR_LICENSE>', 'root')
            line = line.replace("['demoData'] = 'no';", "['demoData'] = '" + install_demo_data + "';")
            print(line, end='')
        config_file.close()

        return tmp_config


    def __get_vm_item(self, compose_name: str, item_name: str):
        for vm_id, vm_data in self.vms.items():
            if vm_data['compose_name'] == compose_name:
                return vm_data[item_name]

        return ''


    def __check_vms_are_running(self):
        if self.running_vms == 0:
            raise Exception('Have you started your server with the start or fullstart action ?')
