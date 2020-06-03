|buildstatus|_
|coverage|_

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
   [bunga 12:32:00] Connected
   $ df
   MOUNTED ON               TOTAL      USED      FREE
   /                        53 MB      2 MB     51 MB
   /proc                     0 MB      0 MB      0 MB
   /sys                      0 MB      0 MB      0 MB
   /mnt/disk1                7 MB      0 MB      7 MB
   /mnt/disk2                0 MB      0 MB      0 MB
   $

The get subcommand
------------------

Get a file from your system.

.. code-block:: text

   $ bunga get_file init
   $

The put subcommand
------------------

Put a file on your system.

.. code-block:: text

   $ bunga put_file init
   $

The log subcommand
------------------

Stream system logs to your PC.

.. code-block:: text

   $ bunga log
   ...

The monitor subcommand
----------------------

Monitor the system.

.. code-block:: text

   $ bunga monitor
   ...

.. |buildstatus| image:: https://travis-ci.com/eerimoq/bunga.svg?branch=master
.. _buildstatus: https://travis-ci.com/eerimoq/bunga

.. |coverage| image:: https://coveralls.io/repos/github/eerimoq/bunga/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/eerimoq/bunga

.. _Monolinux example project: https://github.com/eerimoq/monolinux-example-project
