.. _requirements:

Requirements
************

OnTask has been developed as a `Django <https://www.djangoproject.com/>`_ application. Django is a high-level, python-based web framework that supports a rich set of functionality typically required in applications like OnTask. As many other web applications, OnTask requires a set of additional libraries for its execution, namely:

- Redis
- PostgreSQL (version 9.5 or later)
- Python 3.9
- Django 3.2
- Additional Django modules listed in the file ``requirements/base.txt``

Some of these requirements are handled using `pip <https://pypi.python.org/pypi/pip>`__ (Python's package index application).

.. _install_redis:

Install and Configure Redis
===========================

Django requires Redis to execute as a daemon in the same machine to cache information about the sessions. No specific changes are required in the code, simply have the server running in the background.

1. Download and install `redis <https://redis.io/>`_.

   Follow the instructions to configure it to be used by Django.

2. Test that it is executing properly in the background (use the ``ping`` command in the command line interface.

.. _install_postgresql:

Install and Configure PostgreSQL
================================

1. Download and install `postgresql <https://www.postgresql.org/>`_.

#. Create the role ``ontask`` with the command ``createuser``. The role should be able to create new databases but not new roles and you should define a password for the user (use ``createuser --interactive -W``).

#. Adjust the access configuration in postgresql (in the configuration file ``pg_hba.conf``) to allow the newly created user to access databases locally.

#. Create a new database with name ``ontask`` with the ``createdb`` command.

#. Use the client application ``psql`` to verify that the user has access the newly created database and can create and delete a new table and run regular queries. Test the connection with the following command::

     psql -h 127.0.0.1 -U ontask -W ontask

   If the client does not connect to the database, review your configuration options.

#. The libraries required by OnTask will install some Python packages compiling the soure and one of them uses the development libraries from PostgreSQL. If you are using a linux distribution, make sure you install the package ``postgresql-server-dev-all``.

.. _install_python:

Install Python 3
================

In the following sections we assume that you can open a command line interpreter and you can execute the two python interpreter for version 3.

1. Install `python <https://www.python.org/>`_

#. Verify that the interpreter can run and has the right version (3) using the command line interpreter (either ``python --version`` or ``python3 --version``).

#. Install `pip <https://pip.pypa.io/en/stable/>`__ (the package may be called ``python3-pip`` for Python 3). This tool will be used to install additional libraries required to execute OnTask.

#. Some python libraries will require compiling source code, so make sure the package python3.7-dev is also installed.

