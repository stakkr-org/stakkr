import os
import sys

from distutils.core import setup
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from stakkr.setup import StakkrPostInstall

setup(
    name='stakkr-recompose',
    version='2.0',
    description='A configurable stack based on docker to run any combination of services (PHP, MySQL, Apache, Nginx, Mongo, etc..)',
    url='http://github.com/edyan/stakkr',
    author='Emmanuel Dyan',
    author_email='emmanueldyan@gmail.com',
    license='Apache 2.0',
    packages=['stakkr'],
    py_modules=['stakkr'],
    entry_points='''[console_scripts]
stakkr=stakkr.cli:main
docker-clean=stakkr.docker_clean:main
stakkr-compose=stakkr.stakkr_compose:cli''',
    include_package_data=True,
    install_requires=[
        'clint',
        'click', 'click-plugins',
        'docker-compose',
        'configobj',
        'requests>=2.11.0,<2.12'
        ],
    cmdclass={'install': StakkrPostInstall},
)
