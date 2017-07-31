Custom Services
==================================


Overview
-------------------
If you need a specific service that is not included in stakkr by default, you can add
a yml file into ``services/`` directory.


Write a Service
-------------------
A ``stakkr`` service respects the ``docker-compose`` standard, plus a few customizations.


Some rules:

- The ``yaml`` file must be named with the same name than the service
- That name will help to define the name of the service in ``conf/compose.ini``
- You are free to add everything you want to ``conf/compose.ini``
- A configuration parameter such as ``php.ram`` generates an environment variable that looks like ``DOCKER_PHP_RAM``.



Example
~~~~~~~~~
Let's make an nginx service. The file will be located into ``services/`` as
``nginx.yml``.


.. code:: yaml

    version: '2'

    services:
        nginx:
            image: nginx:${DOCKER_NGINX_VERSION}
            mem_limit: ${DOCKER_NGINX_RAM}
            container_name: ${COMPOSE_PROJECT_NAME}_nginx
            hostname: ${COMPOSE_PROJECT_NAME}_nginx
            networks: [stakkr]
            ports:
                - "8080:80"


Now in ``conf/compose.ini``:

.. code:: cfg

    services=nginx
    nginx.version=1.13-alpine
    nginx.ram=256M


Restart:

.. code:: bash

    $ stakkr restart --recreate
    $ stakkr status


To run a command, use the standard ``exec`` wrapper:

.. code:: bash

    $ stakkr exec nginx cat /etc/nginx/nginx.conf
