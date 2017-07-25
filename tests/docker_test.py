import os
import subprocess
import sys
import unittest

from stakkr import docker

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


# https://docs.python.org/3/library/unittest.html#assert-methods
class DockerTest(unittest.TestCase):
    def test_container_running(self):
        """Make sure, even in another directory, the venv base dir is correct"""
        try:
            subprocess.call(['docker', 'stop', 'pytest'])
            subprocess.call(['docker', 'rm', 'pytest'])
        except Exception:
            pass

        cmd = ['docker', 'run', '-d', '--rm', '--name', 'pytest', 'nginx:stable-alpine']
        subprocess.call(cmd)

        self.assertTrue(docker.container_running('pytest'))


    def test_container_not_running(self):
        """Make sure, even in another directory, the venv base dir is correct"""
        try:
            subprocess.call(['docker', 'stop', 'pytest'])
            subprocess.call(['docker', 'rm', 'pytest'])
        except Exception:
            pass

        self.assertFalse(docker.container_running('pytest'))


    def test_get_container_info(self):
        """
        Start docker compose with another configuration file, then
        extract VM Info

        """
        try:
            self._exec_cmd(['docker', 'stop', 'test_php'])
            self._exec_cmd(['docker', 'rm', 'test_php'])
        except Exception:
            pass

        cmd = ['stakkr-compose', '-c', base_dir + '/static/config_valid.ini', 'up', '-d']
        self._exec_cmd(cmd)
        cts = docker.get_running_containers('test', base_dir + '/static/config_valid.ini')
        self.assertIs(len(cts), 2)
        for ct_id, ct_info in cts.items():
            if ct_info['name'] == 'test_maildev':
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

        self.assertTrue(docker._container_in_network('test_php', 'test_stakkr'))
        self.assertTrue(docker._network_exists('test_stakkr'))
        self.assertFalse(docker._container_in_network('test_php', 'bridge'))

        cmd = ['stakkr-compose', '-c', base_dir + '/static/config_valid.ini', 'stop']
        self._exec_cmd(cmd)
        self._exec_cmd(['docker', 'stop', 'test_php'])
        self._exec_cmd(['docker', 'rm', 'test_php'])

        with self.assertRaisesRegex(SystemError, 'Container test_php does not seem to exist'):
            docker._container_in_network('test_php', 'bridge')

        self._exec_cmd(['stakkr', 'stop'])
        self._exec_cmd(['stakkr', 'dns', 'stop'])
        self._exec_cmd(['docker', 'network', 'rm', 'test_stakkr'])
        self.assertFalse(docker._network_exists('test_stakkr'))


    def test_create_network(self):
        """
        Create a network then a container, attache one to the other
        And verify everything is OK

        """
        try:
            self._exec_cmd(['docker', 'stop', 'pytest'])
            self._exec_cmd(['docker', 'rm', 'pytest'])
        except Exception:
            pass

        if docker._network_exists('nw_pytest'):
            self._exec_cmd(['docker', 'network', 'rm', 'nw_pytest'])

        cmd = ['docker', 'run', '-d', '--rm', '--name', 'pytest', 'nginx:stable-alpine']
        subprocess.call(cmd)

        self.assertTrue(docker.container_running('pytest'))
        self.assertFalse(docker._container_in_network('pytest', 'pytest'))
        self.assertFalse(docker._network_exists('nw_pytest'))
        self.assertTrue(docker.create_network('nw_pytest'))
        self.assertFalse(docker.create_network('nw_pytest'))
        self.assertTrue(docker.add_container_to_network('pytest', 'nw_pytest'))
        self.assertFalse(docker.add_container_to_network('pytest', 'nw_pytest'))
        self.assertTrue(docker._container_in_network('pytest', 'nw_pytest'))
        try:
            self._exec_cmd(['docker', 'stop', 'pytest'])
            self._exec_cmd(['docker', 'rm', 'pytest'])
        except Exception:
            pass

        if docker._network_exists('nw_pytest'):
            self._exec_cmd(['docker', 'network', 'rm', 'nw_pytest'])


    def test_get_container_info_not_exists(self):
        self.assertIs(None, docker._extract_container_info('not_exists', 'not_exists'))


    def _exec_cmd(self, cmd: list):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()


if __name__ == "__main__":
    unittest.main()
