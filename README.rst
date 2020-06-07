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

The get_file subcommand
-----------------------

Get a file from your system.

.. code-block:: text

   $ bunga get_file /root/wire.ko

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
