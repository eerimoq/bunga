|buildstatus|_

Bunga
=====

Control and monitor your system.

Project homepage: https://github.com/eerimoq/bunga

Installation
------------

.. code-block:: python

   $ pip install bunga

The shell subcommand
--------------------

Connect to your system (in this case the `Monolinux example project`_)
and execute the ``df`` command.

.. code-block:: text

   $ bunga shell
   Connected.
   $ df
   MOUNTED ON               TOTAL      USED      FREE
   /                        53 MB      2 MB     51 MB
   /proc                     0 MB      0 MB      0 MB
   /sys                      0 MB      0 MB      0 MB
   /mnt/disk1                7 MB      0 MB      7 MB
   /mnt/disk2                0 MB      0 MB      0 MB
   OK
   $

The get subcommand
------------------

Get a file from your system.

.. code-block:: text

   $ bunga get init

The put subcommand
------------------

Put a file on your system.

.. code-block:: text

   $ bunga put init

.. |buildstatus| image:: https://travis-ci.com/eerimoq/bunga.svg?branch=master
.. _buildstatus: https://travis-ci.com/eerimoq/bunga

.. _Monolinux example project: https://github.com/eerimoq/monolinux-example-project
