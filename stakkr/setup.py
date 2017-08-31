"""
Setup post actions, used in the main setup.py
"""

import os
import shutil
import sys
from setuptools.command.install import install
from stakkr import package_utils


try:
    import click

    @click.command(help="""Initialize for the first time stakkr by copying
templates and directory structure""")
    @click.option('--force', '-f', help="Force recreate directories structure",
                  is_flag=True)
    def init(force: bool):
        """CLI Entry point, when initializing stakkr manually"""

        config_file = package_utils.get_venv_basedir() + '/conf/compose.ini'
        if os.path.isfile(config_file) and force is False:
            click.secho('Config file (conf/compose.ini) already present. Leaving.', fg='yellow')
            return

        msg = 'Config file (conf/compose.ini) not present, do not forget to create it'
        click.secho(msg, fg='yellow')
        _post_install(force)
except ImportError:
    def init():
        """If click is not installed, display that message"""

        print('Stakkr has not been installed yet')
        sys.exit(1)


def _post_install(force: bool = False):
    print('Post Installation : create templates')

    venv_dir = package_utils.get_venv_basedir()
    # If already installed don't do anything
    if os.path.isfile(venv_dir + '/conf/compose.ini'):
        return

    required_dirs = [
        'conf/mysql-override',
        'conf/php-fpm-override',
        'conf/xhgui-override',
        'data',
        'home/www-data',
        'home/www-data/bin',
        'logs',
        'plugins',
        'services',
        'www'
    ]
    for required_dir in required_dirs:
        _create_dir(venv_dir, required_dir, force)

    required_tpls = [
        '.env',
        'bash_completion',
        'conf/compose.ini.tpl',
        'conf/mysql-override/mysqld.cnf',
        'conf/php-fpm-override/example.conf',
        'conf/php-fpm-override/README',
        'conf/xhgui-override/config.php',
        'home/www-data/.bashrc'
    ]
    for required_tpl in required_tpls:
        _copy_file(venv_dir, required_tpl, force)


def _create_dir(venv_dir: str, dir_name: str, force: bool):
    dir_name = venv_dir + '/' + dir_name.lstrip('/')
    if os.path.isdir(dir_name) and force is False:
        return

    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)


def _copy_file(venv_dir: str, source_file: str, force: bool):
    full_path = package_utils.get_file('tpls', source_file)
    dest_file = venv_dir + '/' + source_file
    if os.path.isfile(dest_file) and force is False:
        print('  - {} exists, do not overwrite'.format(source_file))
        return

    print('  - {} written'.format(source_file))
    try:
        shutil.copy(full_path, dest_file)
    except Exception:
        msg = "Error trying to copy {} .. check that the file is there ...".format(full_path)
        print(msg, file=sys.stderr)


class StakkrPostInstall(install):
    """Class called by the main setup.py"""

    def __init__(self, *args, **kwargs):
        super(StakkrPostInstall, self).__init__(*args, **kwargs)

        try:
            package_utils.get_venv_basedir()
            _post_install(False)
        except OSError:
            msg = 'You must run setup.py from a virtualenv if you want to have '
            msg += 'the templates installed'
            print(msg)

