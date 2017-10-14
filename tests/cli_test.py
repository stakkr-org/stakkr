import os
import subprocess
import sys
import unittest

from click.testing import CliRunner
from stakkr.cli import stakkr

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_dir + '/../')


class CliTest(unittest.TestCase):
    cmd_base = ['stakkr', '-c', base_dir + '/static/config_valid.ini']

    def test_no_arg(self):
        result = CliRunner().invoke(stakkr)
        self.assertEqual(0, result.exit_code)
        self.assertEqual('Usage: stakkr [OPTIONS] COMMAND [ARGS]', result.output[:38])


    def test_bad_arg(self):
        result = CliRunner().invoke(stakkr, ['hello-world'])
        self.assertEqual(2, result.exit_code)
        self.assertEqual('Usage: stakkr [OPTIONS] COMMAND [ARGS]', result.output[:38])

        res_out = result.output[-38:].strip()
        self.assertEqual('Error: No such command "hello-world".', res_out)


    def test_pull(self):
        exec_cmd(self.cmd_base + ['start', '--pull'])


    def test_recreate(self):
        exec_cmd(self.cmd_base + ['start', '--recreate'])


    def test_pull_recreate(self):
        exec_cmd(self.cmd_base + ['start', '--pull', '--recreate'])


    def test_debug_mode(self):
        exec_cmd(self.cmd_base + ['start'])

        cmd = self.cmd_base + ['--debug', 'console', 'portainer']
        res = exec_cmd(cmd)
        self.assertEqual(res['stdout'], '')
        self.assertRegex(res['stderr'], r'.*OSError: Could not find a shell for that container*', ' '.join(cmd))
        self.assertIs(res['status'], 1)


    def test_bad_config(self):
        res = exec_cmd([
            'stakkr', '-c', base_dir + '/static/config_invalid.ini', 'start'])
        self.assertRegex(res['stderr'], r'.*Failed validating.*')
        self.assertRegex(res['stderr'], r'.*project_name.*Missing.*')
        self.assertRegex(res['stderr'], r'.*php\.version.*unacceptable.*')
        self.assertEqual(res['stdout'], '')
        self.assertIs(res['status'], 1)


    def test_console_no_ct(self):
        exec_cmd(self.cmd_base + ['start'])
        cmd = self.cmd_base + ['console']

        res = exec_cmd(cmd)
        self.assertRegex(res['stderr'], r'Usage: stakkr console \[OPTIONS\] CONTAINER.*')
        self.assertEqual(res['stdout'], '')
        self.assertIs(res['status'], 2)


    def test_console(self):
        exec_cmd(self.cmd_base + ['start'])

        cmd = self.cmd_base + ['console', 'mysql']
        res = exec_cmd(cmd)
        self.assertRegex(res['stderr'], r'.*Invalid value: invalid choice: mysql\. \(choose from.*')
        self.assertEqual(res['stdout'], '')
        self.assertIs(res['status'], 2)

        exec_cmd(self.cmd_base + ['stop'])

        cmd = self.cmd_base + ['console', 'php']
        res = exec_cmd(cmd)
        self.assertEqual(res['stdout'], '')
        self.assertRegex(res['stderr'], r'.*Have you started your server with the start action.*')
        self.assertIs(res['status'], 1)


    def test_exec_php(self):
        exec_cmd(self.cmd_base + ['dns', 'stop'])
        exec_cmd(self.cmd_base + ['start'])

        # Check for PHP Version
        # TODO make it work under windows (problem with TTY)
        if os.name != 'nt':
            cmd = self.cmd_base + ['exec', '--no-tty', 'php', 'php', '-v']
            res = exec_cmd(cmd)
            self.assertRegex(res['stdout'], r'.*The PHP Group.*', 'stderr was : ' + res['stderr'])
            self.assertEqual(res['stderr'], '')
            self.assertIs(res['status'], 0)

        exec_cmd(self.cmd_base + ['stop'])
        cmd = self.cmd_base + ['exec', 'php', 'php', '-v']
        res = exec_cmd(cmd)
        self.assertEqual(res['stdout'], '')
        self.assertRegex(res['stderr'], r'.*Have you started your server with the start action.*')
        self.assertIs(res['status'], 1)


    def test_mysql(self):
        exec_cmd(self.cmd_base + ['start'])

        cmd = self.cmd_base + ['mysql', '--version']
        res = exec_cmd(cmd)
        self.assertEqual(res['stdout'], '')
        self.assertRegex(res['stderr'], r'.*Invalid value: invalid choice: mysql.*')
        self.assertIs(res['status'], 2)


    def test_restart_stopped(self):
        exec_cmd(self.cmd_base + ['stop'])
        exec_cmd(self.cmd_base + ['dns', 'stop'])
        cmd = self.cmd_base + ['restart']

        # Restart
        res = exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'RESTARTING.*your stakkr services.*STOPPING.*STARTING.*your stakkr services.*For Maildev.*')
        self.assertIs(res['status'], 0)

        # Check it's fine
        cmd = self.cmd_base + ['status']
        res = exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'Container\s*IP\s*Ports\s*Image.*')
        self.assertRegex(res['stdout'], '.*192.168.*')
        self.assertRegex(res['stdout'], '.*test_maildev.*')
        self.assertRegex(res['stdout'], '.*test_php.*')
        self.assertIs(res['status'], 0)


    def test_restart_started(self):
        exec_cmd(self.cmd_base + ['start'])
        exec_cmd(self.cmd_base + ['dns', 'stop'])

        cmd = self.cmd_base + ['restart']

        # Restart
        res = exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'RESTARTING.*your stakkr services.*STOPPING.*your stakkr services.*STARTING.*your stakkr services.*For Maildev.*')
        self.assertIs(res['status'], 0)

        # Check it's fine
        cmd = self.cmd_base + ['status']
        res = exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'Container\s*IP\s*Ports\s*Image.*')
        self.assertRegex(res['stdout'], '.*192.168.*')
        self.assertRegex(res['stdout'], '.*test_maildev.*')
        self.assertRegex(res['stdout'], '.*test_php.*')
        self.assertIs(res['status'], 0)


    def test_start(self):
        exec_cmd(self.cmd_base + ['stop'])
        exec_cmd(self.cmd_base + ['dns', 'stop'])

        cmd = self.cmd_base + ['start']

        # Start
        res = exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'\[STARTING\].*your stakkr services.*For Maildev.*')
        # Problem with scrutinizer : can't get a correct status
        # TODO check and fix it later
        if 'SCRUTINIZER_API_ENDPOINT' not in os.environ:
            self.assertIs(res['status'], 0)

        # Again ....
        res = exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'\[STARTING\].*your stakkr services.*\[INFO\] stakkr is already started.*')
        self.assertIs(res['status'], 0)


    def test_status(self):
        exec_cmd(self.cmd_base + ['dns', 'stop'])
        exec_cmd(self.cmd_base + ['start'])
        cmd = self.cmd_base + ['status']

        # Status OK
        res = exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], r'Container\s*IP\s*Ports\s*Image.*')
        self.assertRegex(res['stdout'], '.*192.168.*')
        self.assertRegex(res['stdout'], '.*test_maildev.*')
        self.assertRegex(res['stdout'], '.*test_php.*')
        self.assertIs(res['status'], 0)

        # With DNS
        if os.name not in ['nt']:
            res = exec_cmd(self.cmd_base + ['dns', 'start'])
            self.assertEqual(res['stderr'], '')
            self.assertRegex(res['stdout'], r'.*\[START\].*DNS forwarder.*')

            res = exec_cmd(cmd)
            self.assertEqual(res['stderr'], '')
            self.assertRegex(res['stdout'], r'.*Container\s*HostName\s*Ports\s*Image.*')
            self.assertNotRegex(res['stdout'], '.*192.168.*')
            self.assertRegex(res['stdout'], '.*test_maildev.*')
            self.assertRegex(res['stdout'], '.*test_php.*')
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
        self.assertRegex(res['stderr'], r'.*Have you started your server with the start action.*')
        self.assertIs(res['status'], 1)


    def tearDownClass():
        cli = CliTest()
        exec_cmd(cli.cmd_base + ['stop'])
        exec_cmd(cli.cmd_base + ['dns', 'stop'])


def exec_cmd(cmd: list):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    status = p.returncode
    stdout = stdout.decode().strip().replace('\n', '')
    stderr = stderr.decode().strip().replace('\n', '')

    return {'stdout': stdout, 'stderr': stderr, 'status': status}


if __name__ == "__main__":
    unittest.main()
