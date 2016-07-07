#!/usr/bin/python3
from setuptools import setup, find_packages

setup(name='docker-lamp',
      version='0.1',
      description='A stack based on docker to run PHP Applications',
      url='http://github.com/inetprocess/lamp',
      author='Emmanuel Dyan',
      author_email='emmanuel.dyan@inetprocess.com',
      license='Apache 2.0',
      packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
      install_requires=['clint'])
