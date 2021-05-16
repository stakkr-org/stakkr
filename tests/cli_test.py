import os
import subprocess
import sys
import pytest
import unittest
from shutil import rmtree
from click.testing import CliRunner
from stakkr.docker_actions import get_client as docker_client, _container_in_network
from stakkr.cli import stakkr

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR + '/../')


class CliTest(unittest.TestCase):
    cmd_base = ['stakkr', '-c', BASE_DIR + '/static/stakkr.yml']

    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd

    def test_no_arg(self):
        result = CliRunner().invoke(stakkr)
        self.assertEqual(0, result.exit_code)
        self.assertEqual('Usage: stakkr [OPTIONS] COMMAND [ARGS]', result.output[:38])

    def test_bad_arg(self):
        """
        Try a unknown command and make sure the result is "no such command"
        """

        result = CliRunner().invoke(stakkr, ['hello-world'])
        self.assertEqual(2, result.exit_code)
        self.assertEqual('Usage: stakkr [OPTIONS] COMMAND [ARGS]', result.output[:38])

        regex = r"Error: No such command ['\"]+hello-world['\"]+."
        self.assertRegex(result.output[-38:].strip(), regex)

    def test_pull(self):
        exec_cmd(self.cmd_base + ['start', '--pull'])

    def test_recreate(self):
        exec_cmd(self.cmd_base + ['start', '--recreate'])

    def test_pull_recreate(self):
        exec_cmd(self.cmd_base + ['start', '--pull', '--recreate'])

    def test_debug_mode(self):
        exec_cmd(self.cmd_base + ['start', '-r'])

        res = exec_cmd(self.cmd_base + ['--debug', 'console', 'portainer'])
        self.assertEqual(res['stdout'], '')
        regex = r'.*OSError: Could not find a shell for that container*'
        self.assertRegex(res['stderr'], regex)
        self.assertIs(res['status'], 1)

    def test_bad_config(self):
        res = exec_cmd([
            'stakkr', '-c', BASE_DIR + '/static/config_invalid.yml', 'start'])
        self.assertRegex(res['stderr'], r'.*Failed validating config.*')
        self.assertRegex(res['stderr'], r'.*config_invalid\.yml.*')
        self.assertRegex(res['stderr'], r".*'toto' was unexpected.*")
        self.assertRegex(res['stdout'], r".*STARTING.* your stakkr services")
        self.assertIs(res['status'], 1)

    def test_console_no_ct(self):
        exec_cmd(self.cmd_base + ['start'])

        res = exec_cmd(self.cmd_base + ['console'])
        self.assertRegex(res['stderr'], r'Usage: stakkr console \[OPTIONS\] CONTAINER.*')
        self.assertEqual(res['stdout'], '')
        self.assertIs(res['status'], 2)

    def test_console(self):
        exec_cmd(self.cmd_base + ['start'])

        res = exec_cmd(self.cmd_base + ['console', 'mysql'])
        self.assertRegex(res['stderr'], r"Error: Invalid value: 'mysql' is not one of.+")
        self.assertEqual(res['stdout'], '')
        self.assertIs(res['status'], 2)

        exec_cmd(self.cmd_base + ['stop'])

        res = exec_cmd(self.cmd_base + ['console', 'php'])
        self.assertEqual(res['stdout'], '')
        self.assertRegex(res['stderr'], r'.+Have you started stakkr with the start action.+')
        self.assertIs(res['status'], 1)

    def test_exec_php(self):
        exec_cmd(self.cmd_base + ['start'])

        # Check for PHP Version
        # TODO make it work under windows (problem with TTY)
        if os.name != 'nt':
            res = exec_cmd(self.cmd_base + ['exec', '--no-tty', 'php', 'php', '-v'])
            self.assertRegex(res['stdout'], r'.*The PHP Group.*', 'stderr was : ' + res['stderr'])
            self.assertEqual(res['stderr'], '')
            self.assertIs(res['status'], 0)

        exec_cmd(self.cmd_base + ['stop'])
        res = exec_cmd(self.cmd_base + ['exec', 'php', 'php', '-v'])
        self.assertEqual(res['stdout'], '')
        self.assertRegex(res['stderr'], r'.*Have you started stakkr with the start action.*')
        self.assertIs(res['status'], 1)

    def test_restart_stopped(self):
        self._proxy_start_check_not_in_network()

        exec_cmd(self.cmd_base + ['stop'])

        # Restart
        res = exec_cmd(self.cmd_base + ['restart'])
        self.assertEqual(res['stderr'], '')
        regex = r'RESTARTING.*your stakkr services.*STOPPING.*STARTING.*your stakkr services.*For Maildev.*'
        self.assertRegex(res['stdout'], regex)
        self.assertIs(res['status'], 0)

        # Proxy is in network now
        self.assertIs(True, _container_in_network('proxy_stakkr', 'static_stakkr'))

        # Check it's fine
        res = exec_cmd(self.cmd_base + ['status'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'Container\s*IP\s*Url\s*Image.*')
        self.assertRegex(res['stdout'], '.*maildev.static.localhost.*')
        self.assertRegex(res['stdout'], '.*static_maildev.*')
        self.assertRegex(res['stdout'], '.*static_php.*')
        self.assertRegex(res['stdout'], '.*No traefik rule.*php.*')
        self.assertIs(res['status'], 0)

    def test_restart_started(self):
        exec_cmd(self.cmd_base + ['stop'])
        self._proxy_start_check_not_in_network()

        exec_cmd(self.cmd_base + ['start'])
        # Proxy is in network now
        self.assertIs(True, _container_in_network('proxy_stakkr', 'static_stakkr'))

        # Restart
        res = exec_cmd(self.cmd_base + ['restart'])
        self.assertEqual(res['stderr'], '')
        regex = r'RESTARTING.*your stakkr.*STOPPING.*your stakkr.*STARTING.*your stakkr services.*For Maildev.*'
        self.assertRegex(res['stdout'], regex)
        self.assertIs(res['status'], 0)

        # Check it's fine
        res = exec_cmd(self.cmd_base + ['status'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'Container\s*IP\s*Url\s*Image.*')
        self.assertRegex(res['stdout'], '.*maildev.static.localhost.*')
        self.assertRegex(res['stdout'], '.*static_maildev.*')
        self.assertRegex(res['stdout'], '.*static_php.*')
        self.assertRegex(res['stdout'], '.*No traefik rule.*php.*')
        self.assertIs(res['status'], 0)

        # Proxy is in network
        self.assertIs(True, _container_in_network('proxy_stakkr', 'static_stakkr'))

    def test_start(self):
        self._proxy_start_check_not_in_network()

        exec_cmd(self.cmd_base + ['stop'])

        cmd = self.cmd_base + ['start']

        # Start
        res = exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'\[STARTING\].*your stakkr services.*For Maildev.*')
        # Problem with scrutinizer : can't get a correct status
        # TODO check and fix it later
        if 'SCRUTINIZER_API_ENDPOINT' not in os.environ:
            self.assertIs(res['status'], 0)

        # Proxy is in network now
        self.assertIs(True, _container_in_network('proxy_stakkr', 'static_stakkr'))

        # Again ....
        res = exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        regex = r'\[STARTING\].*your stakkr services.*\[INFO\] stakkr is already started.*'
        self.assertRegex(res['stdout'], regex)
        self.assertIs(res['status'], 0)

    def test_start_single(self):
        exec_cmd(self.cmd_base + ['stop'])

        cmd = self.cmd_base + ['start', 'php']

        # Start
        res = exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'\[STARTING\].*your stakkr services.*edyan/php.*')
        self.assertNotRegex(res['stdout'], r'\[STARTING\].*your stakkr services.*For Maildev.*')
        # Problem with scrutinizer : can't get a correct status
        # TODO check and fix it later
        if 'SCRUTINIZER_API_ENDPOINT' not in os.environ:
            self.assertIs(res['status'], 0)

        # Again ....
        res = exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        regex = r'\[STARTING\].*your stakkr services.*\[INFO\] service php is already started.*'
        self.assertRegex(res['stdout'], regex)
        self.assertIs(res['status'], 0)

    def test_stop_single(self):
        exec_cmd(self.cmd_base + ['stop'])

        # Start
        res = exec_cmd(cmd=self.cmd_base + ['start', 'php'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'\[STARTING\].*your stakkr services.*edyan/php.*')
        self.assertNotRegex(res['stdout'], r'\[STARTING\].*your stakkr services.*For Maildev.*')
        # Problem with scrutinizer : can't get a correct status
        # TODO check and fix it later
        if 'SCRUTINIZER_API_ENDPOINT' not in os.environ:
            self.assertIs(res['status'], 0)

        # Stop the wrong one
        res = exec_cmd(self.cmd_base + ['stop', 'maildev'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'\[STOPPING\].*your stakkr services.*')
        self.assertIs(res['status'], 0)

        res = exec_cmd(self.cmd_base + ['status'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'.*edyan/php.*')
        self.assertIs(res['status'], 0)

        # Stop the right one
        res = exec_cmd(self.cmd_base + ['stop', 'php'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'\[STOPPING\].*your stakkr services.*')
        self.assertIs(res['status'], 0)

        res = exec_cmd(self.cmd_base + ['status'])
        self.assertEqual(res['stderr'], '')
        self.assertEqual(res['stdout'], r'[INFO] stakkr is currently stopped')
        self.assertNotRegex(res['stdout'], r'.*edyan/php.*')
        self.assertIs(res['status'], 0)

    def test_status(self):
        exec_cmd(self.cmd_base + ['stop'])
        exec_cmd(self.cmd_base + ['start'])

        cmd = self.cmd_base + ['status']

        # Status OK
        res = exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'Container\s*IP\s*Url\s*Image.*')
        self.assertRegex(res['stdout'], '.*maildev.static.localhost.*')
        self.assertRegex(res['stdout'], '.*static_maildev.*')
        self.assertRegex(res['stdout'], '.*static_php.*')
        self.assertRegex(res['stdout'], '.*No traefik rule.*php.*')
        self.assertIs(res['status'], 0)

        exec_cmd(self.cmd_base + ['stop'])

        # Status not ok , it has been stopped
        res = exec_cmd(cmd)
        self.assertEqual(res['stdout'], r'[INFO] stakkr is currently stopped')
        self.assertEqual(res['stderr'], '')
        self.assertIs(res['status'], 0)

    def test_stop(self):
        exec_cmd(self.cmd_base + ['start'])
        cmd = self.cmd_base + ['stop']

        # Stop OK
        res = exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'\[STOPPING\].*your stakkr services.*')
        self.assertIs(res['status'], 0)

        # Stop Error : it has been stopped already
        res = exec_cmd(cmd)
        self.assertRegex(res['stdout'], r'\[STOPPING\].*your stakkr services.*')
        self.assertRegex(res['stderr'], r'.*Have you started stakkr with the start action.*')
        self.assertIs(res['status'], 1)

    def test_services_list(self):
        res = exec_cmd(self.cmd_base + ['services'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'.*Available services usable in stakkr.yml.*maildev.*latest.*php.*portainer.*')
        self.assertNotRegex(res['stdout'], r'.*nginx.*')
        self.assertIs(res['status'], 0)

    def test_services_add_bad_service(self):
        res = exec_cmd(self.cmd_base + ['services-add', 'bad_service'])
        self.assertRegex(res['stdout'], r'.*bad_service.*is not a valid repo \(status = 404\).*')
        self.assertEqual(res['stderr'], '')
        self.assertIs(res['status'], 1)

    def test_services_add_service_from_name(self):
        res = exec_cmd(self.cmd_base + ['services-add', 'databases'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'.*Package.*databases.*installed successfully.*')
        self.assertRegex(res['stdout'], r'.*Try stakkr services to see new available services.*')
        self.assertIs(res['status'], 0)

    def test_services_update_service_from_name(self):
        res = exec_cmd(self.cmd_base + ['services-update'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'.*Packages updated')
        self.assertIs(res['status'], 0)

    def test_services_double_install(self):
        rmtree(BASE_DIR + '/static/services/databases', ignore_errors=True)

        res = exec_cmd(self.cmd_base + ['services-add', 'databases'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'.*Package.*databases.*installed successfully')
        self.assertIs(res['status'], 0)

        res = exec_cmd(self.cmd_base + ['services-add', 'databases'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'.*Package "databases" is already installed, updating')
        self.assertIs(res['status'], 0)

    def test_services_add_service_from_url(self):
        rmtree(BASE_DIR + '/static/services/db', ignore_errors=True)

        cmd_opts = ['services-add', 'https://github.com/stakkr-org/services-databases.git', 'db']
        res = exec_cmd(self.cmd_base + cmd_opts)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'.*Package.*databases.*installed successfully')
        self.assertIs(res['status'], 0)

    def test_aliases(self):
        exec_cmd(self.cmd_base + ['-c', BASE_DIR + '/static/config_aliases.yml', 'start'])

        res = exec_cmd([
            'stakkr', '-c', BASE_DIR + '/static/config_aliases.yml', 'phpver', '--no-tty'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r".*PHP 7\.2.*")
        self.assertIs(res['status'], 0)

        res = exec_cmd([
            'stakkr', '-c', BASE_DIR + '/static/config_aliases.yml', 'phptest', '--no-tty'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r"phptest")
        self.assertIs(res['status'], 0)

    def setUpClass():
        """Clean containers and services directory"""
        from docker import client
        from docker.errors import NotFound
        cts = client.from_env().containers.list(all=True)
        for ct in cts:
            try:
                ct.stop()
                ct.remove(v=True, force=True)
            except NotFound:
                pass

        cli = CliTest()

        for service in ['db', 'databases', 'emails', 'php']:
            rmtree(BASE_DIR + '/static/services/' + service, ignore_errors=True)
        exec_cmd(cli.cmd_base + ['services-add', 'php'])
        exec_cmd(cli.cmd_base + ['services-add', 'emails'])

    def tearDownClass():
        cli = CliTest()

        exec_cmd(cli.cmd_base + ['stop'])

        stop_remove_container('static_maildev')
        stop_remove_container('static_php')
        stop_remove_container('static_portainer')

        for service in ['db', 'databases', 'emails', 'php']:
            rmtree(BASE_DIR + '/static/services/' + service, ignore_errors=True)
        exec_cmd(cli.cmd_base + ['services-add', 'php'])
        exec_cmd(cli.cmd_base + ['services-add', 'emails'])

    def _proxy_start_check_not_in_network(self):
        from stakkr.proxy import Proxy
        # First start Proxy to verify it'll be added in the network
        Proxy().stop()
        Proxy().start()
        # Proxy is not connected to network
        self.assertIs(
            False,
            _container_in_network('proxy_stakkr', 'static_stakkr'))


def exec_cmd(cmd: list):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    status = p.returncode
    stdout = stdout.decode().strip().replace('\n', '')
    stderr = stderr.decode().strip().replace('\n', '')

    return {'stdout': stdout, 'stderr': stderr, 'status': status}


def stop_remove_container(ct_name: str):
    from docker.errors import NotFound
    try:
        ct = docker_client().containers.get(ct_name)
        ct.stop()
        ct.remove()
    except NotFound:
        pass


if __name__ == "__main__":
    unittest.main()
