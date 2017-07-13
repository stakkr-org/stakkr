"""Module used by setup.py to find plugins to load with click"""

import pip
import sys

from importlib import import_module
from marina import utils
from os import chdir, listdir, path


def install_prerequisites():
    try:
        import click
    except ImportError:
        pip.main(['install', 'click'])
        pip.main(['install', 'click-plugins'])

    try:
        import clint
    except ImportError:
        pip.main(['install', 'clint'])


def get_plugins():
    """Read the plugins directory, get the subfolders from it and look for .py files"""

    install_prerequisites()

    # Make sure I am at the right place to load the plugins
    chdir(utils.get_venv_basedir())
    if path.isdir('plugins') is False:
        return ''

    folders = _get_subfolders('plugins')

    plugins = []
    for folder in folders:
        plugins = _add_plugin_from_dir(plugins, 'plugins/{}/'.format(folder))

    return sorted(plugins)


def get_plugins_configuration():
    """Write a string understandable by setuptools and click"""

    plugins = get_plugins()

    return '' if len(plugins) is 0 else '[marina.plugins]\n' + '\n'.join(plugins)


def _add_plugin_from_dir(plugins: list, full_path: str):
    files = _get_files_from_folder(full_path)
    for plugin in files:
        module_name = '{}{}'.format(full_path, plugin).replace('/', '.')[:-3]
        try:
            module = import_module(module_name, package=None)
        except Exception as e:
            raise TypeError('Problem importing {} (Reason: {})'.format(module_name, e))

        if hasattr(module, plugin[:-3]):
            plugins.append('{0}={1}:{0}'.format(plugin[:-3], module_name))

    return plugins


def _get_files_from_folder(full_path: str):
    files = listdir(full_path)

    return [filename for filename in files if path.isfile(full_path + filename) and filename.endswith('.py')]


def _get_subfolders(directory: str):
    subfolders = listdir(directory)

    return [folder for folder in subfolders if path.isdir('{}/{}'.format(directory, folder))]
