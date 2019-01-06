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
like ``docker-compose.yml`` with super power (and is super simple !).

It means that a directory with a ``stakkr.yml`` is a complete stack.

Installation and configuration
------------------------------
To install stakkr, you need python 3 and docker.

- For **Ubuntu**, install python3 with ``sudo apt -y install python3-pip python3-setuptools python3-virtualenv python3-wheel``. You can download Docker from : https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/

- For **MacOS**, install python3 from https://www.python.org/downloads/mac-osx/ (3.6 is ok) or with brew with ``brew install python3``. Then docker from https://docs.docker.com/docker-for-mac/install/.

- For **Windows**, install python3 from https://www.python.org/downloads/ and docker from https://docs.docker.com/docker-for-windows/install/


Then :

.. code:: shell

    $ python -m pip --no-cache-dir install stakkr
    $ mkdir my_project
    $ cd my_project
    $ stakkr-init

Init copies some templates and creates base directories to work.


Development
-----------

Setup your env
~~~~~~~~~~~~~~

To develop stakkr, you have to create a virtual environment :

.. code:: shell

    $ git clone git@github.com:stakkr-org/stakkr.git stakkr
    $ cd stakkr
    $ python3 -m venv venv
    $ source venv/bin/activate
    # For Windows use "venv\Scripts\activate"


Then install stakkr and its dependencies :

.. code:: shell

    $ python -m pip install --upgrade pip wheel
    $ python -m pip install -e .
    $ python -m pip install -r requirements-dev.txt
    $ stakkr-init


Run Tests
~~~~~~~~~

.. code:: shell

    $ py.test -c pytest.ini


Generate that doc
~~~~~~~~~~~~~~~~~

.. code:: shell

    $ cd docs
    $ sphinx-autobuild . _build_html


Try stakkr from a docker in docker container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The code below starts a dind container and init a symfony app :

.. code:: shell

    $ docker run --rm -ti docker:dind ash
    $ apk add curl git python3
    $ python3 -m pip install --upgrade https://github.com/stakkr-org/stakkr/archive/master.zip
    $ mkdir /app
    $ cd /app
    $ stakkr-init symfony
