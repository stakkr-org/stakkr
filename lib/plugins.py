"""Module used by setup.py to find plugins to load with click"""

from importlib import import_module
from os import listdir, path


def get_plugins_configuration():
    plugins = get_plugins()

    return '' if len(plugins) is 0 else '[marina.plugins]\n' + '\n'.join(plugins)


def get_plugins():
    """Read the plugins directory, get the subfolders from it and look for .py files"""

    if path.isdir('plugins') is False:
        return ''

    folders = _get_subfolders('plugins')

    plugins = []
    for folder in folders:
        plugins = _add_plugin_from_dir(plugins, 'plugins/{}/'.format(folder))

    return sorted(plugins)


def _add_plugin_from_dir(plugins: list, full_path: str):
    files = _get_files_from_folder(full_path)
    for plugin in files:
        module_name = '{}{}'.format(full_path, plugin).replace('/', '.')[:-3]
        module = import_module(module_name, package=None)
        if hasattr(module, plugin[:-3]):
            plugins.append('{0}={1}:{0}'.format(plugin[:-3], module_name))

        return plugins


def _get_files_from_folder(full_path: str):
    files = listdir(full_path)

    return [filename for filename in files if path.isfile(full_path + filename) and filename.endswith('.py')]


def _get_subfolders(directory: str):
    subfolders = listdir(directory)

    return [folder for folder in subfolders if path.isdir('{}/{}'.format(directory, folder))]
