Usage
==================================

Before running any command
---------------------------------
.. IMPORTANT::
    You have to be in a virtual environement. To verify that, check that your 
	prompt starts with something like ``(xyz_marina)``

If you have autoenv, and if you kept the name of the virtualenv as
described above, just enter the directory, and it’ll be automatically activated.
Else:

.. code:: bash

    $ source ${PWD##*/}_marina/bin/activate

To leave that environment:

.. code:: bash

    $ deactivate



Get Help
--------
To get a list of commands do ``marina --help`` and to get help for a
specific command : ``marina start --help``



CLI Reference
----------------
.. click:: marina:marina
   :prog: marina
   :show-nested:

.. click:: docker_clean:clean
   :prog: docker-clean
   :show-nested:
