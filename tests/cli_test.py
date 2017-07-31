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
        self._exec_cmd(self.cmd_base + ['start', '--pull'])


    def test_recreate(self):
        self._exec_cmd(self.cmd_base + ['start', '--recreate'])


    def test_pull_recreate(self):
        self._exec_cmd(self.cmd_base + ['start', '--pull', '--recreate'])


    def test_debug_mode(self):
        self._exec_cmd(self.cmd_base + ['start'])

        cmd = self.cmd_base + ['--debug', 'exec', 'notexist', 'bad']
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stdout'], '')
        self.assertRegex(res['stderr'], '.*Exception: notexist does not seem to be started.*')
        self.assertIs(res['status'], 1)


    def test_bad_config(self):
        res = self._exec_cmd([
            'stakkr', '-c', base_dir + '/static/config_invalid.ini', 'start'])
        self.assertRegex(res['stderr'], '.*Failed validating.*')
        self.assertRegex(res['stderr'], '.*project_name.*Missing.*')
        self.assertRegex(res['stderr'], '.*php\.version.*unacceptable.*')
        self.assertEqual(res['stdout'], '')
        self.assertIs(res['status'], 1)


    def test_console_no_ct(self):
        self._exec_cmd(self.cmd_base + ['start'])
        cmd = self.cmd_base + ['console']

        res = self._exec_cmd(cmd)
        self.assertRegex(res['stderr'], 'Usage: stakkr console \[OPTIONS\] CONTAINER.*')
        self.assertEqual(res['stdout'], '')
        self.assertIs(res['status'], 2)


    def test_console(self):
        self._exec_cmd(self.cmd_base + ['start'])

        cmd = self.cmd_base + ['console', 'mysql']
        res = self._exec_cmd(cmd)
        self.assertRegex(res['stderr'], '.*mysql does not seem to be started.*')
        self.assertEqual(res['stdout'], '')
        self.assertIs(res['status'], 1)

        self._exec_cmd(self.cmd_base + ['stop'])

        cmd = self.cmd_base + ['console', 'php']
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stdout'], '')
        self.assertRegex(res['stderr'], '.*Have you started your server with the start action.*')
        self.assertIs(res['status'], 1)


    def test_refresh_plugins(self):
        cmd = self.cmd_base + ['refresh-plugins']
        res = self._exec_cmd(cmd)
        self.assertRegex(res['stdout'], '.*No plugin to add*')
        self.assertEqual(res['stderr'], '')
        self.assertIs(res['status'], 0)


    def test_exec_php(self):
        self._exec_cmd(self.cmd_base + ['dns', 'stop'])
        self._exec_cmd(self.cmd_base + ['start'])

        # Check for PHP Version
        cmd = self.cmd_base + ['exec', 'php', 'php', '-v']
        res = self._exec_cmd(cmd)
        self.assertRegex(res['stdout'], '.*The PHP GroupZend Engine.*')
        self.assertEqual(res['stderr'], '')
        self.assertIs(res['status'], 0)

        self._exec_cmd(self.cmd_base + ['stop'])
        cmd = self.cmd_base + ['exec', 'php', 'php', '-v']
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stdout'], '')
        self.assertRegex(res['stderr'], '.*Have you started your server with the start action.*')
        self.assertIs(res['status'], 1)


    def test_mysql(self):
        self._exec_cmd(self.cmd_base + ['start'])

        cmd = self.cmd_base + ['mysql', '--version']
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stdout'], '')
        self.assertRegex(res['stderr'], '.*mysql does not seem to be started.*')
        self.assertIs(res['status'], 1)


    def test_restart_stopped(self):
        self._exec_cmd(self.cmd_base + ['stop'])
        self._exec_cmd(self.cmd_base + ['dns', 'stop'])
        cmd = self.cmd_base + ['restart']

        # Restart
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], 'RESTARTING.*your stakkr services.*STOPPING.*STARTING.*your stakkr services.*For Maildev.*')
        self.assertIs(res['status'], 0)

        # Check it's fine
        cmd = self.cmd_base + ['status']
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], 'Container\s*IP\s*Ports\s*Image.*')
        self.assertRegex(res['stdout'], '.*192.168.*')
        self.assertRegex(res['stdout'], '.*test_maildev.*')
        self.assertRegex(res['stdout'], '.*test_php.*')
        self.assertIs(res['status'], 0)


    def test_restart_started(self):
        self._exec_cmd(self.cmd_base + ['start'])
        self._exec_cmd(self.cmd_base + ['dns', 'stop'])

        cmd = self.cmd_base + ['restart']

        # Restart
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], 'RESTARTING.*your stakkr services.*STOPPING.*your stakkr services.*STARTING.*your stakkr services.*For Maildev.*')
        self.assertIs(res['status'], 0)

        # Check it's fine
        cmd = self.cmd_base + ['status']
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], 'Container\s*IP\s*Ports\s*Image.*')
        self.assertRegex(res['stdout'], '.*192.168.*')
        self.assertRegex(res['stdout'], '.*test_maildev.*')
        self.assertRegex(res['stdout'], '.*test_php.*')
        self.assertIs(res['status'], 0)


    def test_start(self):
        self._exec_cmd(self.cmd_base + ['stop'])
        self._exec_cmd(self.cmd_base + ['dns', 'stop'])

        cmd = self.cmd_base + ['start']

        # Start
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], '\[STARTING\].*your stakkr services.*For Maildev.*')
        self.assertIs(res['status'], 0)

        # Again ....
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], '\[STARTING\].*your stakkr services.*\[INFO\] stakkr is already started.*')
        self.assertIs(res['status'], 0)


    def test_status(self):
        self._exec_cmd(self.cmd_base + ['dns', 'stop'])
        self._exec_cmd(self.cmd_base + ['start'])
        cmd = self.cmd_base + ['status']

        # Status OK
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], 'Container\s*IP\s*Ports\s*Image.*')
        self.assertRegex(res['stdout'], '.*192.168.*')
        self.assertRegex(res['stdout'], '.*test_maildev.*')
        self.assertRegex(res['stdout'], '.*test_php.*')
        self.assertIs(res['status'], 0)

        # With DNS
        res = self._exec_cmd(self.cmd_base + ['dns', 'start'])
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], '.*\[START\].*DNS forwarder.*')

        res = self._exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], '.*Container\s*HostName\s*Ports\s*Image.*')
        self.assertNotRegex(res['stdout'], '.*192.168.*')
        self.assertRegex(res['stdout'], '.*test_maildev.*')
        self.assertRegex(res['stdout'], '.*test_php.*')
        self.assertIs(res['status'], 0)

        self._exec_cmd(self.cmd_base + ['stop'])

        # Status not ok , it has been stopped
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stdout'], '[INFO] stakkr is currently stopped')
        self.assertEqual(res['stderr'], '')
        self.assertIs(res['status'], 0)


    def test_run_deprecated(self):
        self._exec_cmd(self.cmd_base + ['start'])
        cmd = self.cmd_base + ['run', 'php', '-v']
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], '\[DEPRECATED\].*You must use either.*')
        self.assertIs(res['status'], 0)


    def test_stop(self):
        self._exec_cmd(self.cmd_base + ['start'])
        cmd = self.cmd_base + ['stop']

        # Stop OK
        res = self._exec_cmd(cmd)
        self.assertEqual(res['stderr'], '')
        self.assertRegex(res['stdout'], '\[STOPPING\].*your stakkr services.*')
        self.assertIs(res['status'], 0)

        # Stop Error : it has been stopped already
        res = self._exec_cmd(cmd)
        self.assertRegex(res['stdout'], '\[STOPPING\].*your stakkr services.*')
        self.assertRegex(res['stderr'], '.*Have you started your server with the start action.*')
        self.assertIs(res['status'], 1)


    def tearDownClass():
        cli = CliTest()
        cli._exec_cmd(cli.cmd_base + ['stop'])
        cli._exec_cmd(cli.cmd_base + ['dns', 'stop'])


    def _exec_cmd(self, cmd: list):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        status = p.returncode

        stdout = stdout.decode().strip().replace('\n', '')
        stderr = stderr.decode().strip().replace('\n', '')

        return {'stdout': stdout, 'stderr': stderr, 'status': status}
