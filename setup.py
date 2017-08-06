import os
import sys

from distutils.core import setup
from stakkr.setup import StakkrPostInstall

here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)

extra_packages = []
if os.name == 'nt':
    extra_packages.append('pypiwin32')


setup(
    name='stakkr',
    version='3.3',
    description='A configurable stack based on docker to run any combination of services (PHP, MySQL, Apache, Nginx, Mongo, etc..)',
    long_description=""".. image:: https://raw.githubusercontent.com/edyan/stakkr/master/docs/stakkr-logo.png
    :width: 200px
    :align: center

Overview
==================================
.. image:: https://scrutinizer-ci.com/g/edyan/stakkr/badges/quality-score.png?b=master
.. image:: https://scrutinizer-ci.com/g/edyan/stakkr/badges/build.png?b=master


Stakkr is a a docker recompose tool that uses docker compose to easily
create / maintain a stack of services, for example for web development.

Via a configuration file you can setup the required services and
let stakkr link and start everything for you.

It works only in CLI.

Full Documentation: http://stakkr.readthedocs.org


Versions
=============
.. IMPORTANT::
   Stakkr has known 3 versions and 3 names :
   - 1.x : it was called ``docker-lamp`` and was made to setup an Apache + PHP + MySQL Environment
   - 2.x : it was called ``marina`` (nice name!) and was made to have a stack build around various
   services.
   - 3.x : current version (and probably future ones) , now ``stakkr``. Why changing its name again ?
   Because marina is used by various people and therefore our tool could add more confusion.



What does that do exactly ?
==============================
If you have heard of Docker, you know that when you need to build a full environment
with multiple services that are linked, you either have to do everything manually or
use `docker-compose`. The second solution is the best _but_ it implies that you need, for each
environment, to change your parameters, choose your images, learn the `docker-compose` command
line tool, etc ... In brief, it's not very flexible and hard to learn.

Stakkr will help you, via a very simple configuration file and a predefined list of services
(that can be extended by plugins) to build a complete environment. Plus, to control it in command line.
It makes use of docker easy.

Last, but not the least, it's highly configurable and each service mounts a volume to have a persistence
of data. You can even, if you want, add more directives on some services (change the `php.ini` for
example and chose your versions (PHP 5.3 or 5.6 or 7.1 or anything else).


Examples
==============
You can combine services as you want to have :

- A **Dev LAMP stack** (Apache + MySQL 5.7 + PHP 7.1 with xdebug and xhprof) ...
  and if suddenly you want to test your code with PHP 7.1,
  change it in `conf/compose.ini`, restart, it's done !
- Or Apache 2.4 + PHP 5.6 + MongoDB for a **production environment**
- Or **only Maildev**
- Or **only PHP 5.4 + ElasticSearch**
- etc...""",
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
        'docker', 'docker-compose',
        'configobj',
        'requests>=2.11.0,<2.12'
        ] + extra_packages,
    cmdclass={'install': StakkrPostInstall},
    classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: Apple Public Source License',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.5',
    ],
    keywords='docker,docker-compose,python,stack,development,lamp',
)
