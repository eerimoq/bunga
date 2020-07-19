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

.. image:: https://github.com/eerimoq/bunga/raw/master/docs/shell.png

The log subcommand
------------------

Stream logs from your system to your PC.

.. image:: https://github.com/eerimoq/bunga/raw/master/docs/log.png

The plot subcommand
-------------------

Plot any command output over time. The plot below shows the CPU load.

.. code-block:: text

   $ bunga plot cpu

.. image:: https://github.com/eerimoq/bunga/raw/master/docs/plot.gif

Press ``h`` or ``?`` to show the help.

Define plots in ``~/.bunga-plot.json``.

.. code-block:: json

   {
       "cpu": {
           "title": "CPU [%]",
           "command": "cat proc/stat",
           "pattern": "cpu\\s+\\d+\\s+\\d+\\s+\\d+\\s+(\\d+)",
           "algorithm": "delta",
           "interval": 2,
           "timespan": 60
           "scale": -1,
           "offset": 100,
           "y-min": 0,
           "y-max": 100
       },
       "uptime": {
           "title": "Uptime [s]",
           "command": "cat proc/uptime",
           "max-values": 1000
       }
   }

The execute subcommand
----------------------

Execute given command, ``ls`` in the example below, and print its
output.

.. code-block:: text

   $ bunga execute ls
   mnt etc proc init root dev

The get_file subcommand
-----------------------

Get a file from your system.

.. code-block:: text

   $ bunga get_file README.rst
   100%|█████████████████████████████████████| 1.19k/1.19k [00:00<00:00, 74.1kB/s]

The put_file subcommand
-----------------------

Put a file on your system.

.. code-block:: text

   $ bunga put_file README.rst
   100%|█████████████████████████████████████| 1.19k/1.19k [00:00<00:00, 24.1kB/s]

.. |buildstatus| image:: https://travis-ci.com/eerimoq/bunga.svg?branch=master
.. _buildstatus: https://travis-ci.com/eerimoq/bunga

.. |coverage| image:: https://coveralls.io/repos/github/eerimoq/bunga/badge.svg?branch=master
.. _coverage: https://coveralls.io/github/eerimoq/bunga

.. _Monolinux example project: https://github.com/eerimoq/monolinux-example-project
