Plugins development
==================================


Write a plugin
-------------------
To write a plugin you need to create a folder in the plugins/ directory that contains your commands. Each file with a
`.py` extension will be taken as a plugin. The main function should be named exactly like the file. Of course you can use any module included in marina during your developments (click, clint, lib.command, lib.docker, etc...). 

Example for a file that is in `plugins/my_command/hi.py`:

.. code-block:: python

    import click

    
    @click.command(help="Example")
    def hi():
        print('Hi!')


Once your plugin has been written you need to re-run:

.. code-block:: bash

    $ marina refresh-plugins


Install a plugin
----------------------
To install a plugin

.. code-block:: bash

    $ cd plugins/
    $ git clone https://github.com/xyz/marina-myplugin myplugin
    $ marina refresh-plugins


You can, for example install the sugarcli plugin:

.. code-block:: bash

    $ cd plugins/
    $ git clone https://github.com/inetprocess/marina-sugarcli sugarcli
    $ marina refresh-plugins


As well as the composer one:

.. code-block:: bash

    $ cd plugins/
    $ git clone https://github.com/edyan/marina-composer composer
    $ marina refresh-plugins


Define services in your plugins
-----------------------------------
By creating a `services/` directory you can either override or create new services with your plugins.
Example: `plugins/myplugin/services/mysql.yml` will override the default mysql service while `plugins/myplugin/services/nginx.yml` will define a new service.

Each service added by a plugin must be added in `compose.ini` to be started.


List of existing plugins
-----------------------------------
* `marina-composer <https://github.com/edyan/marina-composer>`_ : Download and run composer
* `marina-sugarcli <https://github.com/inetprocess/marina-sugarcli>`_ : Download and run sugarcli
* `marina-phing <https://github.com/edyan/marina-phing>`_ : Download and run Phing
