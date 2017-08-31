Installation
========================================


Docker
----------
You must have Docker installed on your computer. Pick the right version for your OS from https://www.docker.com/community-edition


Prerequisites
----------------
.. WARNING::
	You need to first install OS packages for Python3: ``pip``, ``setuptools``, ``virtualenv`` and (optionally) `autoenv <https://github.com/kennethreitz/autoenv>`_ on your OS.

	Also, to use docker for Linux as a normal user, you need to add your user to the ``docker`` group (see the documentation)


Example of installation of the dependencies on Ubuntu:

.. code:: shell

    $ sudo apt-get -y install python3-pip python3-setuptools python3-virtualenv virtualenv
    $ sudo pip3 install --upgrade pip
    $ sudo pip3 install autoenv


Stakkr
----------

There are 2 ways to intall Stakkr.

1. The easy way
~~~~~~~~~~~~~~~~~~
Stakkr is usable as a library, it's clean, you have a very beautiful tree
once installed, and it's **recommended**. You can install as many stakkrs that you need.
Just be careful to set different names and networks in `conf/compose.ini`

1.1 Installation under Linux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For Ubuntu, you can download Docker from : https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/

.. code:: shell

    $ mkdir mydev
    $ cd mydev
    $ virtualenv -p /usr/bin/python3 mydev_stakkr
    $ source mydev_stakkr/bin/activate
    $ pip --no-cache-dir install stakkr

It'll run a ``post_install`` script that copy some templates / create base directories to work.

If you have installed ``autoenv``, add into your ``.bashrc``:

.. code:: shell

    source `which activate.sh`



1.2 Installation under Windows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First install python3 from https://www.python.org/downloads/ and
docker from https://docs.docker.com/docker-for-windows/install/

.. code:: shell

    > pip install virtualenv
    > mkdir mydev
    > cd mydev
    > virtualenv venv
    > venv\Scripts\activate
    > pip install stakkr


.. WARNING::
	There are known limitations under windows : First the DNS won't work and Second, `stakkr` has to create a route and change a few parameters inside MobyLinux.


1.3 Installation under MacOSX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First install python3 from https://www.python.org/downloads/mac-osx/ (3.6 is ok) and
docker from https://docs.docker.com/docker-for-mac/install/


.. code:: shell

    $ mkdir mydev
    $ cd mydev
    $ pyvenv-3.6 mydev_stakkr
    $ source mydev_stakkr/bin/activate
    $ pip install stakkr


.. WARNING::
	WIP : I am currently trying to test it on Mac .... but it's not done yet


1.4 Development version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you want to install the dev version, you can do the following :

.. code:: shell

    $ pip install git+https://github.com/edyan/stakkr.git



2. The old way
~~~~~~~~~~~~~~~~
Stakkr gets installed by cloning the github repo .... *not recommended if you don't develop on it*.

You can clone the repository as many times as you want as you can have
multiple instances at the same time. A good practice is too have one
clone for one project or one clone for projects with the same versions
of PHP / MySQL / Elasticsearch, etc ...

.. code:: shell

    $ git clone https://github.com/edyan/stakkr myenv


Once cloned, you can run the ``install.sh`` script made for Ubuntu
(tested on 16.04) that will install the dependencies:

.. code:: shell

    $ cd myenv
    $ ./install.sh


Development
--------------

To develop, use the 2nd way to install Stakkr then :

.. code:: shell

    $ pip install -r requirements-dev.txt


To generate that doc :

.. code:: shell

    $ cd docs
    $ sphinx-autobuild . _build_html
