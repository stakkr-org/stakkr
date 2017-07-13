import os
import shutil

from distutils.core import setup
from marina import package_utils
from setuptools.command.install import install


def _post_install():
    return


class MarinaPostInstall(install):
    def run(self):
        install.run(self)
        self._post_install()


    def _post_install(self):
        self.venv_dir = package_utils.get_venv_basedir()

        required_dirs = [
            'conf',
            'conf/mysql-override',
            'conf/php-fpm-override',
            'conf/xhgui-override',
            'home',
            'home/www-data',
            'home/www-data/bin',
            'logs',
            'plugins',
            'www'
        ]
        for required_dir in required_dirs:
            self._create_dir(required_dir)

        required_tpls = [
            'conf/compose.ini.tpl',
            'conf/mysql-override/mysqld.cnf',
            'conf/php-fpm-override/example.conf',
            'conf/php-fpm-override/README',
            'conf/xhgui-override/config.php',
            'home/www-data/.bashrc'
        ]
        for required_tpl in required_tpls:
            self._copy_file(required_tpl)


    def _create_dir(self, dir_name: str):
        dir_name = self.venv_dir + '/' + dir_name.lstrip('/')
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)


    def _copy_file(self, source_file: str):
        full_path = package_utils.get_file('tpls', source_file)
        dest_file = self.venv_dir + '/' + source_file
        if not os.path.isfile(dest_file):
            try:
                shutil.copy(full_path, dest_file)
            except Exception:
                self.warn("Met an error trying to copy {} .. check that the file is there ...".format(full_path))


setup(
    name='marina',
    version='2.0',
    description='A stack based on docker to run PHP Applications',
    url='http://github.com/edyan/marina',
    author='Emmanuel Dyan',
    author_email='emmanueldyan@gmail.com',
    license='Apache 2.0',
    packages=['marina'],
    py_modules=['marina'],
    entry_points='''[console_scripts]
marina=marina.cli:main
docker-clean=marina.docker_clean:main''',
    scripts=['bin/marina-compose'],
    include_package_data=True,
    install_requires=[
        'clint',
        'click', 'click-plugins',
        'docker-compose',
        'configobj',
        'requests>=2.11.0,<2.12'
        ],
    cmdclass={'install': MarinaPostInstall},
)
