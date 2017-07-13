Installation
========================================


Docker
----------
You must have Docker installed on your computer.

Example for Ubuntu: https://docs.docker.com/engine/installation/ubuntulinux/


Marina
----------
Marina gets installed by cloning the github repo.

You can clone the repository as many times as you want as you can have
multiple instances at the same time. A good practice is too have one
clone for one project or one clone for projects with the same versions
of PHP / MySQL / Elasticsearch, etc ...

.. code:: shell

    $ git clone https://github.com/edyan/marina


Prerequisites
-------------

Automatic Installation
~~~~~~~~~~~~~~~~~~~~~~

Once cloned, you can run the ``install.sh`` script made for Ubuntu
(tested on 16.04) that will install the dependencies:

.. code:: shell

    $ cd marina
    $ ./install.sh

Manual Installation
~~~~~~~~~~~~~~~~~~~

If you want to manually install the dependencies, first install OS packages for Python3: ``pip``, ``setuptools``
and ``virtualenv``.


Then:

-  Install ``autoenv`` (Read https://github.com/kennethreitz/autoenv).
   Example:

   .. code:: shell

       $ pip3 install autoenv

-  Create the virtualenv and activate it:

   .. code:: shell

       $ virtualenv -p /usr/bin/python3 ${PWD##*/}_marina
       $ source ${PWD##*/}_marina/bin/activate
       $ pip3 install -e .


Development
~~~~~~~~~~~

To develop :

.. code:: shell

    $ pip install -r requirements.txt


And to generate that doc :

.. code:: shell

    $ cd docs
    $ sphinx-autobuild . _build_html
