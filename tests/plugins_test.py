"""
Test usage of plugin
"""

import os
import subprocess
import sys
import unittest
from shutil import rmtree
from stakkr import package_utils
__base_dir__ = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, __base_dir__ + '/../')
__venv_dir__ = package_utils.get_venv_basedir()


class PluginsTest(unittest.TestCase):
    cmd_base = ['stakkr', '-c', __base_dir__ + '/static/config_valid.ini']

    def test_no_plugin_dir(self):
        """Make sure I have the right message when no plugin is present"""

        clean_plugin_dir()
        os.rmdir(__venv_dir__ + '/plugins')

        cmd = self.cmd_base + ['refresh-plugins']
        res = exec_cmd(cmd)
        self.assertRegex(res['stdout'], '.*Adding plugins from plugins.*')
        self.assertRegex(res['stdout'], '.*No plugin to add*')
        self.assertEqual(res['stderr'], '')
        self.assertIs(res['status'], 0)

        os.mkdir(__venv_dir__ + '/plugins')

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

        folder = __venv_dir__ + '/plugins/empty_plugin'
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

        folder = __venv_dir__ + '/plugins/test_bad_plugin'
        os.mkdir(folder)

        # Add setup
        with open(folder + '/setup.py', 'w') as file:
            file.write(r"""from setuptools import setup

setup(
    name='StakkrTestPlugin',
    version='3.5',
    packages=['test_plugin'],
    entry_points='''
        [stakkr.plugins]
        test_plugin=test_plugin.core:my_test
    '''
)
""")

        cmd = self.cmd_base + ['refresh-plugins']
        res = exec_cmd(cmd)
        self.assertRegex(res['stdout'], 'Adding plugins from plugins.*')
        self.assertRegex(res['stderr'], 'Command .* failed with error code 1')
        self.assertIs(res['status'], 1)

        rmtree(folder)

    def test_plugin_ok(self):
        """Install a good plugin and test it"""

        clean_plugin_dir()

        folder = __venv_dir__ + '/plugins/test_plugin'
        os.mkdir(folder)
        os.mkdir(folder + '/test_plugin')

        # Add setup
        with open(folder + '/setup.py', 'w') as file:
            file.write(r"""from setuptools import setup

setup(
    name='StakkrTestPlugin',
    version='3.5',
    packages=['test_plugin'],
    entry_points='''
        [stakkr.plugins]
        test_plugin=test_plugin.core:my_test
    '''
)
""")

        # Add plugin content
        with open(folder + '/test_plugin/core.py', 'w') as file:
            file.write(r"""import click

@click.command(name="hello-world")
@click.pass_context
def my_test(ctx):
    print('Hello test !')
""")

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

    def tearDownClass(self):
        clean_plugin_dir()


def clean_plugin_dir():
    if not os.path.isdir(__venv_dir__ + '/plugins'):
        os.mkdir(__venv_dir__ + '/plugins')

    if os.path.isdir(__venv_dir__ + '/plugins/empty_plugin'):
        os.rmdir(__venv_dir__ + '/plugins/empty_plugin')

    if os.path.isdir(__venv_dir__ + '/plugins/test_plugin'):
        rmtree(__venv_dir__ + '/plugins/test_plugin')

    if os.path.isdir(__venv_dir__ + '/plugins/test_bad_plugin'):
        rmtree(__venv_dir__ + '/plugins/test_bad_plugin')


def exec_cmd(cmd: list):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    status = p.returncode
    stdout = stdout.decode().strip().replace('\n', '')
    stderr = stderr.decode().strip().replace('\n', '')

    return {'stdout': stdout, 'stderr': stderr, 'status': status}


if __name__ == "__main__":
    unittest.main()
