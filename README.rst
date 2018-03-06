.. image:: https://raw.githubusercontent.com/edyan/stakkr/master/docs/stakkr-logo.png
    :width: 200px
    :align: center

Overview
========

.. image:: https://scrutinizer-ci.com/g/edyan/stakkr/badges/quality-score.png?b=master
   :target: https://scrutinizer-ci.com/g/edyan/stakkr/?branch=master
.. image:: https://travis-ci.org/edyan/stakkr.svg?branch=master
   :target: https://travis-ci.org/edyan/stakkr
.. image:: https://img.shields.io/pypi/l/stakkr.svg
   :target: https://pypi.python.org/pypi/stakkr


Stakkr
======


Stakkr is a a docker recompose tool that uses docker compose to easily
create / maintain a stack of services, for example for web development.

Via a configuration file you can setup the required services and let
stakkr link and start everything for you.

It works only in CLI and it's a good replacement to Vagrant.



What does that do exactly ?
===========================

If you have heard of Docker, you know that when you need to build a full
environment with multiple services that are linked, you either have to
do everything manually or use ``docker-compose``. The second solution is
the best *but* it implies that you need, for each environment, to change
your parameters, choose your images, learn the ``docker-compose``
command line tool, etc ... In brief, it's not very flexible and hard to
learn.

Stakkr will help you, via a very simple configuration file and a
predefined list of services (that can be extended by plugins) to build a
complete environment. Plus, to control it in command line. It makes use
of docker easy.

Last, but not the least, it's highly configurable and each service
mounts a volume to have a persistence of data. You can even, if you
want, add more directives on some services (change the ``php.ini`` for
example and chose your versions (PHP 5.3 or 5.6 or 7.1 or anything
else).


Examples
========

You can combine services as you want to have :

- A Dev LAMP stack (Apache + MySQL 5.7 + PHP 7.1 with xdebug and xhprof) ... and if suddenly you want to test your code with PHP 7.1, change it in ``conf/compose.ini``, restart, it's done !

- Or Apache 2.4 + PHP 5.6 + MongoDB for a production environment

- Or only Maildev

- Or only PHP5.4 + ElasticSearch

etc...


Documentation
=============

Read the official documentation on
`ReadTheDocs.org <http://stakkr.readthedocs.org>`__
