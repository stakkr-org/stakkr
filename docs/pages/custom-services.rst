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
Let's make a xyz service. The file will be located into ``services/`` as
``xyz.yml``.


.. code:: yaml

    version: '2.2'

    services:
        xyz:
            image: myself/xyz:${DOCKER_XYZ_VERSION}
            mem_limit: ${DOCKER_XYZ_RAM}
            container_name: ${COMPOSE_PROJECT_NAME}_xyz
            hostname: ${COMPOSE_PROJECT_NAME}_xyz
            networks: [stakkr]
            labels:
                - traefik.frontend.rule=Host:xyz.${COMPOSE_PROJECT_NAME}.${PROXY_DOMAIN}



Now in ``conf/compose.ini``:

.. code:: cfg

    services=xyz
    xyz.version=1.13-alpine # what's in DOCKER_XYZ_VERSION
    xyz.ram=256M # what's in DOCKER_XYZ_RAM


Restart:

.. code:: bash

    $ stakkr restart --recreate
    $ stakkr status


To run a command, use the standard ``exec`` wrapper:

.. code:: bash

    $ stakkr exec xyz cat /etc/xyz/xyz.conf



Build your service instead of using an existing image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When you need to build your own image and use it in stakkr, you just need to add a ``Dockerfile``,
like below, then run ``stakkr-compose build`` each time you need to build it. Once built, a simple
``stakkr start`` is enough to start it.


* ``services/memcached.yml`` file :

.. code:: yaml

    version: '2.2'

    services:
        memcached:
            build: ${COMPOSE_BASE_DIR}/services/memcached
            mem_limit: 1024M
            container_name: ${COMPOSE_PROJECT_NAME}_memcached
            hostname: ${COMPOSE_PROJECT_NAME}_memcached
            networks: [stakkr]



* ``services/memcached/Dockerfile`` file :

.. code:: bash

    FROM memcached:1.5-alpine

    # RUN ... your own logic



* In ``conf/compose.ini`` file, add :

.. code:: cfg

    services=....,memcached
