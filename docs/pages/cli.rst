Usage
==================================

Before running any command
---------------------------------
.. IMPORTANT::
    You have to be in a virtual environement. To verify that, check that your
    prompt starts with something like ``(xyz_stakkr)``

If you have autoenv, and if you kept the name of the virtualenv as
described above, just enter the directory, and it’ll be automatically activated.
Else:

.. code:: bash

    $ source ${PWD##*/}_stakkr/bin/activate

To leave that environment:

.. code:: bash

    $ deactivate



Get Help
--------
To get a list of commands do ``stakkr --help`` and to get help for a
specific command : ``stakkr start --help``



CLI Reference
----------------

.. toctree::
   :maxdepth: 2
   :caption: List of CLI tools:

   cli/docker.rst
   cli/stakkr.rst
   cli/stakkr-init.rst
