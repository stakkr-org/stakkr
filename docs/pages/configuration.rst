Configuration
=============

Copy the file ``conf/compose.ini.tpl`` to ``conf/compose.ini`` and set
the right Configuration parameters.

Everything should be defined in the ``[main]`` section. **Don't use
double quotes to protect your values.**. All values are defined in the
compose.ini.tpl.


Network
-----------------
You can define your own network in compose.ini (``subnet`` and
``gateway``). If you change that, run ``docker-clean`` (**Be Careful: it
removes orphans images, stopped container, etc ...**).


Services
-----------------
You can define the list of services you want to have. Each service
consists of a yml file in the ``services/`` directory. Each container
("Virtual Machine") will have a hostname composed of the project name
and the service name. To reach, for example, the elasticsearch server
from a web application, and if your ``project_name = marina`` use
``marina_elasticsearch`` or to connect to mysql use ``marina_mysql``.
The service names also works (*elasticsearch* and *mysql*)

.. code:: cfg

    ; Comma separated list of services to start, valid values: apache / bonita / elasticsearch / mailcatcher / maildev / mongo / mysql / php / phpmyadmin / xhgui
    services=apache,php,mysql

A service can launch a post-start script that has the same name with an
``.sh`` extension (example: ``services/mysql.sh``).


Special case of xhgui service
----------------------------------
To be able to profile your script, add the service xhgui and read the
`documentation`_


Other useful parameters
--------------------------

Project name (will be used as container's prefix). It should be
different for each project.

.. code:: ini

    ; Change Machines names only if you need it
    project_name=marina

PHP Version :

.. code:: ini

    ; Set your PHP version from 5.3 to 7.0 (5.6 by default)
    php.version=7.0

MySQL Password if mysql is defined in the services list:

.. code:: ini

    ; Password set on first start. Once the data exist won't be changed
    mysql.root_password=changeme

Memory assigned to the VMS:

.. code:: ini

    apache.ram=512M
    elasticsearch.ram=512M
    mysql.ram=512M
    php.ram=512M

.. _documentation: https://github.com/edyan/docker-xhgui



Files location
------------------
-  All files served by the web server are located into ``www/``
-  MySQL data is into ``mysql/`` (created on the first run). If you need
   to override the mysql configuration you can put a file in
   ``conf/mysql-override`` with a ``.cnf`` extension. Logs for MySQL are
   also located into ``mysql/`` (slow and error).
-  Mongo data is into ``mongo/`` (created on the first run)
-  Logs for Apache and PHP are located into ``logs/``
-  If you need to override the PHP configuration you can put a file in
   ``conf/php-fpm-override`` with a ``.conf`` extension. The format is
   the fpm configuration files one. Example:
   ``php_value[memory_limit] = 127M``.


Add binaries
------------

You can add binaries (such as phpunit) that will automatically be
available from the PATH by putting it to ``home/www-data/bin/``