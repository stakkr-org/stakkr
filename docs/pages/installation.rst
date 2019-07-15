============
Installation
============


Docker
======
You must have Docker installed on your computer. Pick the right version for your OS from https://www.docker.com/community-edition

.. WARNING::

    Also, to use docker for Linux as a normal user, you need to add your user to the ``docker`` group (see the documentation)


Stakkr
======

Stakkr is installable via pip, system-wide (or for a specific user). It's clean and detects automatically
the config file (``stakkr.yml``) presence in a directory or parent directory to execute commands. ``stakkr.yml`` acts
like ``docker-compose.yml`` with super power (plus, it is super simple !).

It means that a directory with a ``stakkr.yml`` is a complete stack.

Installation and configuration
------------------------------
To install stakkr, you need python 3 and docker.

- For **Ubuntu**, install python3 with ``sudo apt -y install python3-pip python3-setuptools python3-virtualenv python3-wheel``. You can download Docker from : https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/

- For **MacOS**, install python3 from https://www.python.org/downloads/mac-osx/ (3.6 is ok) or with brew with ``brew install python3``. Then docker from https://docs.docker.com/docker-for-mac/install/.

- For **Windows**, install python3 from https://www.python.org/downloads/ and docker from https://docs.docker.com/docker-for-windows/install/


Then :

.. code:: bash

    $ sudo python3 -m pip --no-cache-dir install stakkr

    ###
    # If you want a beta / rc version append "--pre" at the end
    # If you don't want to install it system wide, you can remove "sudo" and append "--user" at the end
    # but to make it work, you'll need to change your $PATH variable
    # That option is recommended when you know how to do and especially for MacOs
    # For windows just run : python -m pip --no-cache-dir install stakkr
    ###
    
    $ mkdir my_project
    $ cd my_project

    ##
    # RECIPE is optional but better to start from an existing one !
    # Examples (see below for the current list) :
    #   stakkr-init wordpress
    #   stakkr-init symfony
    ##

    $ stakkr-init {RECIPE}

``stakkr-init`` copies some templates and creates base directories to work.


Recipes
-------
Currently, the following recipes are available (see https://github.com/stakkr-org/stakkr/tree/master/stakkr/static/recipes) :

* **LAMP** : PHP (latest) + Apache (2.4) + MySQL (5.7) + ``stakkr composer`` to use ``composer`` and ``stakkr mysql`` to use ``mysql``.
* **LEMP** : PHP (latest) + Nginx (latest alpine) + MySQL (5.7) + ``stakkr composer`` to use ``composer`` and ``stakkr mysql`` to use ``mysql``.
* **LEPP** : PHP (latest) + Nginx (latest alpine) + PostgreSQL (latest) + ``stakkr composer`` to use ``composer``.
* **Symfony** : PHP (7.2) + Nginx (latest alpine) + ``stakkr composer`` to use ``composer`` + ``Symfony Framework`` pre-installed.
* **Wordpress** : PHP (7.2) + Apache (2.4) + MySQL (5.7) + ``stakkr wp`` to use ``wp-cli`` + ``Wordpress`` pre-installed.


Use stakkr from a docker dind (Docker-In-Docker) image
------------------------------------------------------

You can else use the ready-to-go Docker Image edyan/stakkr to test the tool.

Be careful that uid and gid of ``stakkr`` user into the container won't be the same than
for your user. The volume will contain files with other permissions.

.. code:: bash

    $ mkdir ~/my_project
    $ docker run -p 80:80 -p 443:443 -v ~/my_project:/home/stakkr/app -d --privileged --rm --name stakkr-dev stakkr/stakkr
    $ docker exec -ti stakkr-dev ash
    $ chown -R stakkr:stakkr /home/stakkr
    $ su - stakkr
    # Create a symfony project from a recipe
    $ cd ~/app
    $ stakkr-init symfony


Now open http://nginx.app.localhost from your browser.


Development
-----------

Setup your env
~~~~~~~~~~~~~~

To develop stakkr, you have to create a virtual environment :

.. code:: bash

    $ git clone git@github.com:stakkr-org/stakkr.git stakkr
    $ cd stakkr
    $ python3 -m venv venv_stakkr
    $ source venv_stakkr/bin/activate
    # For Windows use "venv_stakkr\Scripts\activate"


Then install stakkr and its dependencies :

.. code:: bash

    $ python -m pip install --upgrade pip wheel
    $ python -m pip install -e .
    $ python -m pip install -r requirements-dev.txt
    $ stakkr-init


Run Tests
~~~~~~~~~

.. code:: bash

    $ py.test


Generate that doc
~~~~~~~~~~~~~~~~~

.. code:: bash

    $ cd docs
    $ sphinx-autobuild . _build_html


Try stakkr from a docker in docker container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The code below starts a dind container and init a symfony app :

.. code:: bash

    # From the host
    $ docker run -d --privileged --rm --name stakkr-test docker:dind
    $ docker exec -ti stakkr-test ash

    # From the container
    # Install packages required by stakkr + w3m as a local browser
    $ apk add curl git python3 w3m

    # Install stakkr
    $ python3 -m pip install --upgrade https://github.com/stakkr-org/stakkr/archive/master.zip
    # Stakkr should always be started as another user than root
    $ addgroup stakkr
    $ adduser -s /bin/ash -D -S -G stakkr stakkr
    $ addgroup stakkr root
    $ su - stakkr

    # Create a symfony project from a recipe
    $ mkdir ~/app && cd ~/app
    $ stakkr-init symfony
    # The following command should returns the default symfony page
    $ w3m http://nginx.app.localhost

    # Go further
    $ mkdir ~/wp && cd ~/wp
    $ stakkr-init wordpress
    # The following command should returns wordpress home
    $ w3m http://apache.wp.localhost



Test your local cloned stakkr from a container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The code below starts a dind container, mount stakkr then install it
and init a symfony app. You need to be inside the stakkr cloned repository for that :

.. code:: bash

    # From the host
    $ docker run -d --privileged -v $(pwd):/stakkr-src --rm --name stakkr-test docker:dind
    $ docker exec -ti stakkr-test ash

    # From the container
    # Install packages required by stakkr + w3m as a local browser
    $ apk add --no-cache python3 alpine-sdk curl git openssl-dev python3-dev w3m libffi-dev

    # Install stakkr
    $ python3 -m pip install --upgrade /stakkr-src

    # Then do what you want ...
