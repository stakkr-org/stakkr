Configuration
=============

If you used a recipe, simply edit the ``stakkr.yml`` file manually to change a service version
or set any parameter. Else, copy the file ``stakkr.yml.tpl`` to ``stakkr.yml`` and set
the right configuration parameters you need.

Configuration is validated. Read carefully the message in case of error.

Main configuration parameters should be defined in the ``services`` section.


Services
-----------------
You can define a list of services you want to have. Each service consists of a yml
file in the ``services/`` directory of the source code.
Each container ("Service") will have a hostname which is the ... service name.
To reach, for example, the elasticsearch server from a web application
use ``elasticsearch``. To connect to mysql it's ``mysql``.


Example of a LAMP stack :

.. code:: yaml

      services:
        adminer:
          enabled: true
        mysql:
          enabled: true
          version: 5.7
          ram: 1024M
          root_password: root
        apache:
          enabled: true
        php:
          enabled: true
          version: latest
          ram: 1024M
          blocked_ports: [25, 465, 587]


To have a complete list of services, launch :

.. code:: shell

    $ stakkr services

The parameters are pretty generic, but some services could define new
parameters such as databases for passwords :

.. code:: yaml

      services:
        any_service:
          # Enable it or not. Default false
          enabled: false
          # Version on docker hub
          version: latest
          # Limited as much as possible to keep computer resources usage
          ram: 512M
          # Displayed after stakkr has started
          service_name: Portainer (Docker Webadmin)
          # Same than above
          service_url: http://{}
          # Port to block for outgoing connexions. Requires :
          # - "cap_add: [NET_ADMIN, NET_RAW]" in compose file
          # - iptables on the container
          blocked_ports: []

HTTPS
-----
If you need to work with websites in HTTPS, change the urls to *https://*. If you don't
want to accept the certificate everytime, you can ask chrome to accept all *localhost*
certificates by calling ``chrome://flags/#allow-insecure-localhost`` as a URL.


Network and changes in general
------------------------------
You can define your own network in compose.ini by setting a ``subnet``.
It's optional, and it's probably better to let it like that.

.. WARNING::
   If you change that, run ``docker-clean`` which removes orphans images, stopped container, etc ...

   As we use ``traefik`` as a reverse proxy, no need to expose any ports
   or to access containers directly via their IP.

   Also, if you change any parameter such as an environment variable
   run a ``stakkr restart --recreate`` to make sure that you start from
   a clean environment.


Special case of Elasticsearch
-----------------------------
ElasticSearch needs a few manual commands to start from the version 5.x. Before starting stakkr, do the following :

.. code:: shell

    $ mkdir data/elasticsearch
    $ sudo chown -R 1000:1000 data/elasticsearch
    $ sudo sysctl -w vm.max_map_count=262144


Special case of xhgui service
-----------------------------
To be able to profile your script, add the service xhgui and read the
`documentation`_


Other useful parameters
--------------------------

Project name (will be used as container's prefix). It should be
different for each project.

.. code:: ini

    environment: dev # Environment variables sent to containers

    proxy: # traefik
      enabled: true # By default it's enabled
      domain: localhost # append domain. Example : http://apache.my_project.localhost
      http_port: 80 # Http Port to expose
      https_port: 443 # Https Port to expose

    project_name: '' # detected automatically, usually the main directory name

    subnet: '' # if you really need to override the default network

    uid: # if you really need to set a specific uid for files, current user by default
    gid: # same for gid, current user's group by default


Files location
------------------

Public Files
~~~~~~~~~~~~~~
-  All files served by the web server are located into ``www/``


Services Data
~~~~~~~~~~~~~~~~~
-  MySQL data is into ``data/mysql``
-  Mongo data is into ``data/mongo``
-  ElasticSearch data is into ``data/elasticsearch``
-  Redis data is into ``data/redis``
- ...

Logs
~~~~~~
-  Logs for Apache and PHP are located into ``logs/``
-  Logs for MySQL are located into ``data/mysql/`` (slow and error).

Configuration
~~~~~~~~~~~~~~~
-  If you need to override the PHP configuration you can put a file in
   ``conf/php-fpm-override`` with a ``.conf`` extension. The format is
   the fpm configuration files one. Example:
   ``php_value[memory_limit] = 127M``.
-  If you need to override the mysql configuration you can put a file in ``conf/mysql-override``
   with a ``.cnf`` extension.


Add binaries
------------
You can add binaries (such as phpunit) that will automatically be
available from the PATH by putting it to ``home/www-data/bin/``


.. IMPORTANT::
   You can use ``home/www-data`` to put everyhting you need to keep:
   your shell parameters in `.bashrc`, your ssh keys/config into `.ssh`, etc.
