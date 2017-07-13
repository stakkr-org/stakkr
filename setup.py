from marina.plugins import get_plugins_configuration
from setuptools import setup, find_packages


setup(
    name='Marina',
    version='2.0',
    description='A stack based on docker to run PHP Applications',
    url='http://github.com/inetprocess/marina',
    author='Emmanuel Dyan',
    author_email='emmanuel.dyan@inetprocess.com',
    license='Apache 2.0',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    py_modules=['marina'],
    entry_points='''
        [console_scripts]
        marina=marina:main
        docker-clean=docker_clean:main
        {}
      '''.format(get_plugins_configuration()),
    install_requires=[
        'clint',
        'click', 'click-plugins',
        'requests>=2.11.0,<2.12',
        'docker-compose',
        'configobj'
        ]
)
