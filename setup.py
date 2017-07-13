import os

from marina.plugins import get_plugins_configuration
from setuptools import setup


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
    entry_points='''
        [console_scripts]
        marina=marina.cli:main
        docker-clean=marina.docker_clean:main
        {}
      '''.format(get_plugins_configuration()),
    data_files=[
        (os.getcwd() + '/conf', ['conf/compose.ini.tpl']),
    ],
    package_data={
        '': ['*.ini'],
    },
    install_requires=[
        'clint',
        'click', 'click-plugins',
        'docker-compose',
        'configobj',
        'requests>=2.11.0,<2.12'
        ]
)
