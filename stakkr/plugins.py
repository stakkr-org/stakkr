"""Module used by setup.py to find plugins to load with click"""

import subprocess

from importlib import import_module
from os import listdir, path


def add_plugins():
    """Read the plugins directory, get the subfolders from it and look for .py files"""

    if path.isdir('plugins') is False:
        return []


    folders = _get_subfolders('plugins')

    plugins = []
    for folder in folders:
        plugins = _add_plugin_from_dir(plugins, 'plugins/{}/'.format(folder))

    return sorted(plugins)


def _add_plugin_from_dir(plugins: list, full_path: str):
    files = _get_files_from_folder(full_path)
    for plugin in files:
        plugin_name = full_path.strip('/').split('/')[1]
        try:
            subprocess.check_call(['pip', 'install', '--upgrade', full_path], stdout=subprocess.DEVNULL)
            print('  -> Plugin "{}" added'.format(plugin_name))
            plugins.append(plugin_name)

        except Exception as e:
            raise TypeError('Problem installing {} (Reason: {})'.format(plugin_name[:-3], e))

    return plugins


def _get_files_from_folder(full_path: str):
    files = listdir(full_path)

    return [filename for filename in files if filename == 'setup.py']


def _get_subfolders(directory: str):
    subfolders = listdir(directory)

    return [folder for folder in subfolders if path.isdir('{}/{}'.format(directory, folder))]
