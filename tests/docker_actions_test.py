import os
import subprocess
import sys
import unittest
from stakkr import docker_actions

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


# https://docs.python.org/3/library/unittest.html#assert-methods
class DockerActionsTest(unittest.TestCase):
    def test_container_running(self):
        """Make sure, even in another directory, the venv base dir is correct"""
        try:
            subprocess.call(['docker', 'stop', 'pytest'])
            subprocess.call(['docker', 'rm', 'pytest'])
        except Exception:
            pass

        cmd = ['docker', 'run', '-d', '--rm', '--name', 'pytest', 'nginx:stable-alpine']
        subprocess.call(cmd)

        self.assertTrue(docker_actions.container_running('pytest'))


    def test_container_not_running(self):
        """Make sure, even in another directory, the venv base dir is correct"""
        try:
            subprocess.call(['docker', 'stop', 'pytest'])
            subprocess.call(['docker', 'rm', 'pytest'])
        except Exception:
            pass

        self.assertFalse(docker_actions.container_running('pytest'))


    def test_get_container_info(self):
        """
        Start docker compose with another configuration file, then
        extract VM Info

        """

        cmd = ['stakkr-compose', '-c', base_dir + '/static/config_valid.ini', 'up', '-d', '--force-recreate']
        exec_cmd(cmd)
        numcts, cts = docker_actions.get_running_containers('test')
        self.assertIs(len(cts), 3)
        for ct_id, ct_info in cts.items():
            if ct_info['name'] in ('test_maildev', 'test_portainer'):
                continue

            self.assertTrue('name' in ct_info)
            self.assertTrue('compose_name' in ct_info)
            self.assertTrue('ports' in ct_info)
            self.assertTrue('running' in ct_info)
            self.assertTrue('ip' in ct_info)
            self.assertTrue('image' in ct_info)

            self.assertEqual(ct_info['name'], 'test_php')
            self.assertEqual(ct_info['compose_name'], 'php')
            self.assertTrue(ct_info['running'])
            self.assertEqual(ct_info['ip'][:8], '192.168.')
            self.assertEqual(ct_info['image'], 'edyan/php:7.0')

        self.assertTrue(docker_actions._container_in_network('test_php', 'test_stakkr'))
        self.assertTrue(docker_actions.network_exists('test_stakkr'))
        self.assertFalse(docker_actions._container_in_network('test_php', 'bridge'))

        cmd = ['stakkr-compose', '-c', base_dir + '/static/config_valid.ini', 'stop']
        exec_cmd(cmd)
        exec_cmd(['docker', 'stop', 'test_php'])
        exec_cmd(['docker', 'rm', 'test_php'])

        with self.assertRaisesRegex(LookupError, 'Container test_php does not seem to exist'):
            docker_actions._container_in_network('test_php', 'bridge')

        exec_cmd(['stakkr', 'stop'])
        exec_cmd(['stakkr', 'dns', 'stop'])
        exec_cmd(['docker', 'network', 'rm', 'test_stakkr'])
        self.assertFalse(docker_actions.network_exists('test_stakkr'))


    def test_create_network(self):
        """
        Create a network then a container, attache one to the other
        And verify everything is OK

        """
        try:
            exec_cmd(['docker', 'stop', 'pytest'])
            exec_cmd(['docker', 'rm', 'pytest'])
            exec_cmd(['docker', 'network', 'prune', '-f'])
        except Exception:
            pass

        if docker_actions.network_exists('nw_pytest'):
            exec_cmd(['docker', 'network', 'rm', 'nw_pytest'])

        cmd = ['docker', 'run', '-d', '--rm', '--name', 'pytest', 'nginx:stable-alpine']
        subprocess.call(cmd)

        self.assertTrue(docker_actions.container_running('pytest'))
        self.assertFalse(docker_actions._container_in_network('pytest', 'pytest'))
        self.assertFalse(docker_actions.network_exists('nw_pytest'))

        network_created = docker_actions.create_network('nw_pytest')
        self.assertNotEqual(False, network_created)
        self.assertIs(str, type(network_created))

        self.assertFalse(docker_actions.create_network('nw_pytest'))
        self.assertTrue(docker_actions.add_container_to_network('pytest', 'nw_pytest'))
        self.assertFalse(docker_actions.add_container_to_network('pytest', 'nw_pytest'))
        self.assertTrue(docker_actions._container_in_network('pytest', 'nw_pytest'))
        exec_cmd(['docker', 'stop', 'pytest'])

        if docker_actions.network_exists('nw_pytest'):
            exec_cmd(['docker', 'network', 'rm', 'nw_pytest'])


    def test_get_container_info_not_exists(self):
        self.assertIs(None, docker_actions._extract_container_info('not_exists', 'not_exists'))


    def test_guess_shell_sh(self):
        try:
            exec_cmd(['docker', 'stop', 'pytest'])
        except:
            pass

        cmd = ['docker', 'run', '-d', '--rm', '--name', 'pytest', 'nginx:stable-alpine']
        exec_cmd(cmd)

        shell = docker_actions.guess_shell('pytest')
        self.assertEqual('/bin/sh', shell)

        exec_cmd(['docker', 'stop', 'pytest'])


    def test_guess_shell_bash(self):
        try:
            exec_cmd(['docker', 'stop', 'pytest'])
        except:
            pass

        cmd = ['docker', 'run', '-d', '--rm', '--name', 'pytest', 'nginx']
        exec_cmd(cmd)

        shell = docker_actions.guess_shell('pytest')
        self.assertEqual('/bin/bash', shell)

        exec_cmd(['docker', 'stop', 'pytest'])


    def tearDownClass():
        exec_cmd(['docker', 'rm', 'pytest'])
        exec_cmd(['docker', 'rm', 'test_maildev'])
        exec_cmd(['docker', 'rm', 'test_php'])
        exec_cmd(['docker', 'rm', 'test_portainer'])
        exec_cmd(['docker', 'network', 'rm', 'nw_pytest'])


def exec_cmd(cmd: list):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()


if __name__ == "__main__":
    unittest.main()
