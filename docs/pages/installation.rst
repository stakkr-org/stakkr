Installation
========================================


Docker
----------
You must have Docker installed on your computer.

Example for Ubuntu: https://docs.docker.com/engine/installation/ubuntulinux/


Prerequisites
----------------
.. WARNING::
	You need to first install OS packages for Python3: ``pip``, ``setuptools``, ``virtualenv`` and (optionally) `autoenv <https://github.com/kennethreitz/autoenv>`_ on your OS.


Example of installation of the dependencies on Ubuntu:

.. code:: shell

    $ sudo apt-get -y install python3-pip python3-setuptools python3-virtualenv virtualenv
    $ sudo pip3 install --upgrade pip
    $ sudo pip3 install autoenv


Marina
----------

There are 2 ways to intall Marina.

1. The easy way
~~~~~~~~~~~~~~~~~~
Marina is usable as a library, it's clean, you have a very beautiful tree
once installed, and it's **recommended**. You can install as many marinas that you need.
Just be careful to set different names and networks in `conf/compose.ini`

Installation :

.. code:: shell

    $ mkdir myenv
    $ cd myenv
    $ virtualenv -p /usr/bin/python3 ${PWD##*/}_marina
    $ source ${PWD##*/}_marina/bin/activate
    $ pip install marina

It'll run a `post_install` script that copy some templates / create base directories to work.


If you want to install the dev version, you can do the following : 
.. code:: shell
    $ pip install git+https://github.com/edyan/marina.git



2. The old way
~~~~~~~~~~~~~~~~
Marina gets installed by cloning the github repo .... *not recommended if you don't develop on it*.

You can clone the repository as many times as you want as you can have
multiple instances at the same time. A good practice is too have one
clone for one project or one clone for projects with the same versions
of PHP / MySQL / Elasticsearch, etc ...

.. code:: shell

    $ git clone https://github.com/edyan/marina myenv


Once cloned, you can run the ``install.sh`` script made for Ubuntu
(tested on 16.04) that will install the dependencies:

.. code:: shell

    $ cd myenv
    $ ./install.sh


3. The old way, manually (to develop mainly)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Create the virtualenv and activate it:

   .. code:: shell

       $ virtualenv -p /usr/bin/python3 ${PWD##*/}_marina
       $ source ${PWD##*/}_marina/bin/activate
       $ pip install -e .


Development
--------------

To develop, use the 3rd way to install Marina then :

.. code:: shell

    $ pip install -r requirements.txt


To generate that doc :

.. code:: shell

    $ cd docs
    $ sphinx-autobuild . _build_html
