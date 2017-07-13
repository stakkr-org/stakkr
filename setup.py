from marina.plugins import get_plugins_configuration
from setuptools import setup, find_packages

def get_console_scripts():
    """Guess if we use marina as a package or if it has been cloned"""

    scripts = "[console_scripts]\n"
    try:
        from marina import cli, docker_clean
        scripts += "marina=marina.cli:main\n"
        scripts += "docker-clean=marina.docker_clean:main\n"
    except Exception:
        scripts += "marina=cli:main\n"
        scripts += "docker-clean=docker_clean:main\n"

    return scripts

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
    entry_points='{}{}'.format(get_console_scripts(), get_plugins_configuration()),
    install_requires=[
        'clint',
        'click', 'click-plugins',
        'docker-compose',
        'configobj',
        'requests>=2.11.0,<2.12'
        ]
)
