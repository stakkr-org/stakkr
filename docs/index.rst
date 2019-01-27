.. image:: https://raw.githubusercontent.com/stakkr-org/stakkr/master/docs/stakkr-logo.png
    :width: 200px
    :align: center

Overview
==================================
.. image:: https://scrutinizer-ci.com/g/stakkr-org/stakkr/badges/quality-score.png?b=master
.. image:: https://api.travis-ci.com/stakkr-org/stakkr.svg?branch=master
.. image:: https://img.shields.io/pypi/l/stakkr.svg
   :target: https://pypi.python.org/pypi/stakkr


Stakkr is a a development tool, based on docker-compose, to easily
use a stack of services. For example, if you need a LAMP environment for your
developments, then stakkr is the right tool.

Via a *very simple* configuration file you can setup the required services and
let stakkr link and start everything for you.

Why ``stakkr`` and not docker-compose ?
* To avoid searching for the right image,
* To stop fighting with permissions,
* To do lot of stuff without reading the full docker documentation,
* Also because you need to share your configuration with your team, so you want a portable tool,
* Finally, you want a very simple tool


What does that do exactly ?
==============================
If you have heard of Docker, you know that when you need to build a full environment
with multiple services that are linked, you either have to do everything manually or
use ``docker-compose``. The second solution is the best *but* it implies that you need, for each
environment, to change your parameters, choose your images, learn the ``docker-compose`` command
line tool, etc ... In brief, it's not very flexible and hard to learn.

Stakkr will help you, via a very simple configuration file and a predefined list of services
(that can be extended with aliases and custom services) to build a complete environment. Plus, to control it in command line.
It makes use of docker easy.

Last, but not the least, it's highly configurable and each service mounts a volume to have a persistence
of data. You can even, if you want, add more directives on some services (change the `php.ini` for
example and choose your versions (PHP 5.6 or 7.1 or 7.3 or anything else).


Examples
==============
You can combine services as you want to have :

- A **Dev LAMP stack** (Apache + MySQL 5.7 + PHP 7.2 with xdebug and xhprof) ...
  and if suddenly you want to test your code with PHP 7.0,
  change it in ``stakkr.yml``, restart, it's done !
- Or Apache 2.2 + PHP 5.6 + MySQL 5.5 for a **legacy environment**
- Or **a ready made symfony stack** (with the project initialized!)
- etc...


.. toctree::
   :maxdepth: 1
   :caption: Contents:

   pages/installation.rst
   pages/configuration.rst
   pages/cli.rst
   pages/custom-services.rst
   pages/code.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
