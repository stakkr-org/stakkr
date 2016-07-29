import click
import importlib
import os

from setuptools import setup, find_packages


def get_plugins():
    folders = [folder for folder in os.listdir('plugins') if os.path.isdir('plugins/{}'.format(folder))]

    plugins = []
    for folder in folders:
        full_path = 'plugins/{}/'.format(folder)
        files = [filename for filename in os.listdir(full_path) if os.path.isfile(full_path + filename) and filename.endswith('.py')]
        for plugin in files:
            module_name = '{}{}'.format(full_path, plugin).replace('/', '.')[:-3]
            module = importlib.import_module(module_name, package=None)
            if hasattr(module, plugin[:-3]):
                print(click.style('Loading {} from {}{}'.format(module_name, full_path, plugin), fg='green'))
                plugins.append('{0}={1}:{0}'.format(plugin[:-3], module_name))
            else:
                print(click.style('Could not load {} from {}{}'.format(module_name, full_path, plugin), fg='red'))

    if len(plugins) is 0:
        return ''

    return '[lamp.plugins]\n' + '\n'.join(plugins)


setup(name='docker-lamp',
      version='0.5',
      description='A stack based on docker to run PHP Applications',
      url='http://github.com/inetprocess/lamp',
      author='Emmanuel Dyan',
      author_email='emmanuel.dyan@inetprocess.com',
      license='Apache 2.0',
      packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
      py_modules=['lamp'],
      entry_points='''
        [console_scripts]
        lamp=lamp:main
        {}
      '''.format(get_plugins()),
      install_requires=[
        'clint',
        'click', 'click-plugins',
        'requests'])
