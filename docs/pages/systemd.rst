Systemd integration
==================================

You can integrate stakkr with systemd to have a single
or multiple instances to start on boot.

All command below are executed from the stakkr root folder


Binary
-------

Link the stakkrd wrapper to the ``/usr/bin`` folder, so it is in the exec path.

.. code-block:: console

   $ sudo cp $(pwd)/systemd/bin/stakkrd /usr/bin/stakkrd


Configuration
-------------------

Create folder in the system config dir and link the ``stakkr.conf`` file into this folder, after
setting the right values in the configuration file. You can automatically change it by doing :

.. code-block:: console

    $ echo WDIR=$(pwd) > systemd/conf/stakkr.conf
    $ echo VIRTUALENV_DIR=$VIRTUAL_ENV >> systemd/conf/stakkr.conf


.. code-block:: console

   $ sudo mkdir /etc/stakkr

   $ sudo cp $(pwd)/systemd/conf/stakkr.conf /etc/stakkr/stakkr.conf


Or if there are *multiple* stakkr instances that needs to be controlled

.. code-block:: console

   $ sudo mkdir /etc/stakkr.d

   $ sudo cp $(pwd)/systemd/conf/stakkr.conf /etc/stakkr.d/01-stakkr.conf


Where you repeat the last linking step for each stakkr instance. Be aware of the order if this would be needed for your setup.



Systemd
--------

Link the ``stakkr.service`` file into the systemd system folder and enable the service

.. code-block:: console

   $ sudo cp $(pwd)/systemd/system/stakkr.service /etc/systemd/system/stakkr.service

   $ sudo systemctl enable stakkr

   $ sudo systemctl start stakkr


If you change anything to the ``stakkr.service``, then you need to reload systemd file after the change.

.. code-block:: console

   $ sudo systemctl daemon-reload
