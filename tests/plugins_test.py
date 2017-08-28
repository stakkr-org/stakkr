"""
Test usage of plugin
"""

import os
import subprocess
import sys
import unittest
from shutil import copytree, rmtree
__base_dir__ = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, __base_dir__ + '/../')


class PluginsTest(unittest.TestCase):
    cmd_base = ['stakkr', '-c', __base_dir__ + '/static/config_valid.ini']

    def test_no_plugin_dir(self):
        """Make sure I have the right message when no plugin is present"""

        clean_plugin_dir()
        os.rmdir(__base_dir__ + '/../plugins')

        cmd = self.cmd_base + ['refresh-plugins']
        res = exec_cmd(cmd)
        self.assertRegex(res['stdout'], '.*Adding plugins from plugins.*')
        self.assertRegex(res['stdout'], '.*No plugin to add*')
        self.assertEqual(res['stderr'], '')
        self.assertIs(res['status'], 0)

        os.mkdir(__base_dir__ + '/../plugins')


    def test_no_plugin(self):
        """Make sure I have the right message when no plugin is present"""

        clean_plugin_dir()

        cmd = self.cmd_base + ['refresh-plugins']
        res = exec_cmd(cmd)
        self.assertRegex(res['stdout'], '.*Adding plugins from plugins.*')
        self.assertRegex(res['stdout'], '.*No plugin to add*')
        self.assertEqual(res['stderr'], '')
        self.assertIs(res['status'], 0)


    def test_plugin_empty(self):
        """Create a directory with nothing inside and see if I get the right message"""

        clean_plugin_dir()

        folder = __base_dir__ + '/../plugins/empty_plugin'
        os.mkdir(folder)
        self.assertTrue(os.path.isdir(folder))

        cmd = self.cmd_base + ['refresh-plugins']
        res = exec_cmd(cmd)
        self.assertRegex(res['stdout'], '.*Adding plugins from plugins.*')
        self.assertRegex(res['stdout'], '.*No plugin found in "plugins/empty_plugin/".*')
        self.assertEqual(res['stderr'], '')
        self.assertIs(res['status'], 0)

        os.rmdir(folder)


    def test_bad_plugin(self):
        """Install a bad plugin and check if it works (it shouldn't)"""

        clean_plugin_dir()

        folder = __base_dir__ + '/../plugins/test_bad_plugin'
        copytree(__base_dir__ + '/static/test_bad_plugin', folder)
        self.assertTrue(os.path.isdir(folder))

        cmd = self.cmd_base + ['refresh-plugins']
        res = exec_cmd(cmd)
        self.assertRegex(res['stdout'], 'Adding plugins from plugins.*')
        self.assertRegex(res['stderr'], 'Command .* failed with error code 1')
        self.assertIs(res['status'], 1)

        rmtree(folder)


    def test_plugin_ok(self):
        """Install a good plugin and test it"""

        clean_plugin_dir()

        folder = __base_dir__ + '/../plugins/test_plugin'
        copytree(__base_dir__ + '/static/test_plugin', folder)
        self.assertTrue(os.path.isdir(folder))

        # Refresh plugins, plugin should be added
        cmd = self.cmd_base + ['refresh-plugins']
        res = exec_cmd(cmd)
        self.assertRegex(res['stdout'], '.*Adding plugins from plugins.*')
        self.assertRegex(res['stdout'], '.*Plugin "test_plugin" added.*')
        self.assertEqual(res['stderr'], '')
        self.assertIs(res['status'], 0)

        # Plugin installed, command available !
        cmd = self.cmd_base + ['hello-world']
        res = exec_cmd(cmd)
        self.assertEqual(res['stdout'], 'Hello test !')
        self.assertEqual(res['stderr'], '')
        self.assertIs(res['status'], 0)

        # Now it should remove
        cmd = self.cmd_base + ['refresh-plugins']
        res = exec_cmd(cmd)
        self.assertRegex(res['stdout'], '.*Adding plugins from plugins.*')
        self.assertRegex(res['stdout'], '.*Cleaning "StakkrTestPlugin".*')
        self.assertRegex(res['stdout'], '.*Plugin "test_plugin" added.*')
        self.assertEqual(res['stderr'], '')
        self.assertIs(res['status'], 0)


        rmtree(folder)


    def tearDownClass():
        clean_plugin_dir()


def clean_plugin_dir():
    if os.path.isdir(__base_dir__ + '/../plugins/empty_plugin'):
        os.rmdir(__base_dir__ + '/../plugins/empty_plugin')

    if os.path.isdir(__base_dir__ + '/../plugins/test_plugin'):
        rmtree(__base_dir__ + '/../plugins/test_plugin')

    if os.path.isdir(__base_dir__ + '/../plugins/test_bad_plugin'):
        rmtree(__base_dir__ + '/../plugins/test_bad_plugin')


def exec_cmd(cmd: list):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    status = p.returncode
    stdout = stdout.decode().strip().replace('\n', '')
    stderr = stderr.decode().strip().replace('\n', '')

    return {'stdout': stdout, 'stderr': stderr, 'status': status}


if __name__ == "__main__":
    unittest.main()
