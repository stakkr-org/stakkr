"""Module used by setup.py to find plugins to load with click"""

import re
import subprocess
from os import listdir, path


def add_plugins():
    """Read the plugins directory, get the subfolders from it and look for .py files"""

    if path.isdir('plugins') is False:
        return []

    _remove_plugins()
    folders = _get_subfolders('plugins')

    plugins = []
    for folder in folders:
        plugins = _add_plugin_from_dir(plugins, 'plugins/{}/'.format(folder))

    return sorted(plugins)


def _add_plugin_from_dir(plugins: list, full_path: str):
    files = _get_files_from_folder(full_path)
    if len(files) is 0:
        print('  -> No plugin found in "{}"'.format(full_path))
        return plugins

    plugin_name = full_path.strip('/').split('/')[1]
    try:
        cmd_install = ['pip', 'install', '-e', full_path]
        subprocess.check_call(cmd_install, stdout=subprocess.DEVNULL)
    except Exception as error:
        msg = 'Problem installing {} (Reason: {})'.format(plugin_name[:-3], error)
        raise TypeError(msg)

    print('  -> Plugin "{}" added'.format(plugin_name))
    plugins.append(plugin_name)

    return plugins


def _get_files_from_folder(full_path: str):
    files = listdir(full_path)

    return [filename for filename in files if filename == 'setup.py']


def _get_subfolders(directory: str):
    subfolders = listdir(directory)

    return [folder for folder in subfolders if path.isdir('{}/{}'.format(directory, folder))]


def _remove_plugins():
    cmd = ['pip', 'freeze']
    res = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    regex = re.compile('.*stakkr([0-9a-z]+).*$', re.IGNORECASE)

    for line in res.stdout:
        plugin = re.search(regex, line.decode())
        if plugin is None:
            continue

        plugin_name = 'Stakkr{}'.format(plugin.group(1))
        print('  -> Cleaning "{}"'.format(plugin_name))
        subprocess.check_call(['pip', 'uninstall', '-y', plugin_name], stdout=subprocess.DEVNULL)
