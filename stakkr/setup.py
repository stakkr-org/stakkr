import sys
import os
import shutil

from stakkr import package_utils
from setuptools.command.install import install


venv_dir = package_utils.get_venv_basedir()


def _post_install():
    required_dirs = [
        'conf',
        'conf/mysql-override',
        'conf/php-fpm-override',
        'conf/xhgui-override',
        'data',
        'home',
        'home/www-data',
        'home/www-data/bin',
        'logs',
        'plugins',
        'services',
        'www'
    ]
    for required_dir in required_dirs:
        _create_dir(required_dir)

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
        _copy_file(required_tpl)


def _create_dir(dir_name: str):
    dir_name = venv_dir + '/' + dir_name.lstrip('/')
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)


def _copy_file(source_file: str):
    full_path = package_utils.get_file('tpls', source_file)
    dest_file = venv_dir + '/' + source_file
    if not os.path.isfile(dest_file):
        try:
            shutil.copy(full_path, dest_file)
        except Exception:
            msg = "Met an error trying to copy {} .. check that the file is there ...".format(full_path)
            print(msg, file=sys.stderr)



class StakkrPostInstall(install):
    def run(self):
        install.run(self)
        _post_install()
