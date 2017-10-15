Plugins development
==================================


Write a plugin
-------------------
To write a plugin you need to create a folder in the plugins/ directory that contains
your commands.

.. WARNING::
    Each directory must contain a `setup.py` to be installed as a plugin.
    Check the following link to have more info about how to build a plugin:
    https://github.com/click-contrib/click-plugins/tree/master/example

Of course you can use any module included in stakkr during your developments
(click, clint, stakkr.command, stakkr.docker, stakkr.package_utils, etc...).


Example
~~~~~~~~~
You want to build a simple command that says "Hello". It'll be called _sayhello_
You need to create two files in a `sayhello` directory.

* `plugins/sayhello/setup.py`

.. code-block:: python

    from setuptools import setup


    setup(
        name='StakkrSayHello',
        version='1.0',
        packages=['sayhello'],
        entry_points='''
            [stakkr.plugins]
            sayhello=sayhello.core:hi
        ''')


* And `plugins/sayhello/sayhello/core.py`

.. code-block:: python

    import click


    @click.command(help="Example")
    def hi():
        print('Hi!')


Once your plugin has been installed you need to run:

.. code-block:: bash

    $ stakkr refresh-plugins
    $ stakkr hi


Install a plugin
----------------------
To install a plugin

.. code-block:: bash

    $ cd plugins/
    $ git clone https://github.com/xyz/stakkr-myplugin myplugin
    $ stakkr refresh-plugins


You can, for example install composer plugin:

.. code-block:: bash

    $ cd plugins/
    $ git clone https://github.com/edyan/stakkr-composer composer
    $ stakkr refresh-plugins
    $ cd ../www
    $ stakkr composer


Define services in your plugins
-----------------------------------
By creating a `services/` directory you can either override or create new services with your plugins.
Example: `plugins/myplugin/services/mysql.yml` will override the default mysql service while
`plugins/myplugin/services/nginx.yml` will define a new service.

Each service added by a plugin must be added in `compose.ini` to be started.


Example of a service:

.. code-block:: yaml

    version: '2.2'

    services:
        nginx:
            image: nginx
            container_name: ${COMPOSE_PROJECT_NAME}_nginx
            hostname: ${COMPOSE_PROJECT_NAME}_nginx
            networks: [stakkr]



List of existing plugins
-----------------------------------
* `stakkr-composer <https://github.com/edyan/stakkr-composer>`_ : Download and run composer
* `stakkr-sugarcli <https://github.com/inetprocess/stakkr-sugarcli>`_ : Download and run sugarcli
* `stakkr-phing <https://github.com/edyan/stakkr-phing>`_ : Download and run Phing
* `stakkr-nginx-proxy <https://github.com/inetprocess/stakkr-nginx-proxy>`_ : Nginx proxy
* `stakkr-phpcron <https://github.com/inetprocess/stakkr-phpcron>`_ : PHP + Cron Service
