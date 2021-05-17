Custom Services
===============


Overview
--------
If you need a specific service that is not included in stakkr by default, you can
create your own package and add it to the **services/** directory.


Write a Package
---------------
A ``stakkr`` package adds to stakkr a set of new services. For example, when you add
services via the ``stakkr services-add`` command, it adds a directory into **services/**
that contain one or more services.

Each service respects the ``docker-compose`` standard, plus a few customizations.


Some rules:

- A package comes with its config validation.
- Each ``yaml`` file defining a service must be named with the same name than the service
- The service will be available in ``stakkr.yml`` once defined
- A configuration parameter such as :

.. code-block:: yaml

   memcached:
     ram: 1024M


generates an environment variable with a name like ``DOCKER_MEMCACHED_RAM``. That
variable is usable in the service definition (docker-compose file).



Example
~~~~~~~
Let's make a new nginx service.

1/ We need to define the ``config_schema.yml`` that will validate the service :
See https://json-schema.org

.. code-block:: yaml
   :caption: services/nginx2/config_schema.yml

   ---

   "$schema": http://json-schema.org/draft-04/schema#
   type: object
   properties:
     services:
       type: object
       additionalProperties: false
       properties:
         nginx2:
           type: object
           additionalProperties: false
           properties:
             enabled: { type: boolean }
             version: { type: [string, number] }
             ram: { type: string }
             service_name: { type: string }
             service_url: { type: string }
           required: [enabled, version, ram, service_name, service_url]


2/ Then the ``config_default.yml`` with the default values, some are
required :

.. code-block:: yaml
   :caption: services/nginx2/config_default.yml

   ---

   services:
     nginx2:
       enabled: false # Required and set to false by default
       version: latest
       ram: 256M
       service_name: Nginx (Web Server) # Required for stakkr status message
       service_url: http://{} (works also in https) # Required for stakkr status message


3/ Then the service itself in a **docker-compose/** subdirectory :

.. code-block:: yaml
   :caption: services/nginx2/docker-composer/nginx2.yml

   version: "3.8"

   services:
       nginx2:
           image: edyan/nginx:${DOCKER_NGINX2_VERSION}
           mem_limit: ${DOCKER_NGINX2_RAM}
           container_name: ${COMPOSE_PROJECT_NAME}_nginx2
           hostname: ${COMPOSE_PROJECT_NAME}_nginx2
           networks: [stakkr]
           labels:
               - traefik.frontend.rule=Host:nginx2.${COMPOSE_PROJECT_NAME}.${PROXY_DOMAIN}


4/ Finally, check that it's available and add it to ``stakkr.yml`` :

.. code-block:: shell

   stakkr services


Output should be like :

.. code-block:: shell

   ...
   - mysql (✘)
   - nginx2 (✘)
   - php (✘)
   ...


Now in ``stakkr.yml``

.. code-block:: yaml
   :caption: stakkr.yml

   services:
     nginx2:
       enabled: true
       ram: 1024M


Restart:

.. code-block:: bash

    $ stakkr restart --recreate
    $ stakkr status


To run a command, use the standard ``exec`` wrapper or create an alias:

.. code-block:: bash

    $ stakkr exec nginx2 cat /etc/passwd



Build your service instead of using an existing image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When you need to build your own image and use it in stakkr, you just need to add a ``Dockerfile``,
like below, then run ``stakkr-compose build`` each time you need to build it. Once built, a simple
``stakkr start`` is enough to start it.


Example again with nginx2 :

1/ Create the **services/nginx2/docker-compose/Dockerfile.nginx2** file :

.. code-block:: shell

    FROM edyan/nginx:latest
    # etc...


2/ Change the **services/nginx2/docker-composer/nginx2.yml** file :

.. code-block:: yaml
   :caption: services/nginx2/docker-composer/nginx2.yml

   version: '2.2'

   services:
       nginx2:
           build:
             context: ${COMPOSE_BASE_DIR}/services/nginx2/docker-compose
             dockerfile: Dockerfile.nginx2
           mem_limit: ${DOCKER_NGINX2_RAM}
           container_name: ${COMPOSE_PROJECT_NAME}_nginx2
           hostname: ${COMPOSE_PROJECT_NAME}_nginx2
           networks: [stakkr]
           labels:
               - traefik.frontend.rule=Host:nginx2.${COMPOSE_PROJECT_NAME}.${PROXY_DOMAIN}
