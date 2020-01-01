
.. _upgrading:

Upgrading OnTask
****************

If you are upgrading OnTask from a version lower than 2.8 to 2.8 or later, you need to disable the ``crontab`` used to execute tasks asynchronously from the web server. Starting in version 2.8 those tasks are executed by an application called ``celery`` that is managed using ``supervisor`` (see :ref:`scheduling_tasks`).

Are you upgrading from version < 4.0 to 4.2?
============================================

The upgrade to 4.0 or later requires Python versions 2.7 and 3.6 both installed and available in the system. Django versions 2.0 and later require Python 3 but certain additional libraries used by OnTask have not been fully ported yet and still require the use of Python 2.7. Make sure both versions are available before proceeding to the upgrade.

Are you upgrading from version < 4.3 to 4.3?
============================================

The  upgrade to 4.3 or later no longer requires two versions of Python. It only requires Python 3. Make sure the application is only using version 3.

Are you upgrading to version 5.2?
=================================

Version 5.2 contains a significant reorganization of the file structure in the tool, and as a consequence there are several files that need to be manually relocated:

- The :ref:`configuration file <configuration_file>` needs to be moved from ``src/ontask/settings`` to ``settings``.

- The files in the ``media`` folder need to be moved to ``ontask/media``.

Upgrade Steps
=============

If you have OnTask already configured and running, here are the steps to follow to upgrade to a new version:

- Create a backup of the database to be able to restore the state of the tool before the upgrade process.

- Stop the apache web server.

- Open a terminal and use a command interpreter to execute the following commands.

- Set the current folder of the interpreter to the main project folder.

- Verify that the :ref:`configuration file <configuration_file>` is in the folder ``settings``.

- Pull the code for the new version from the repository::

    git pull

- Refresh the list of requirements::

    pip3 install -r requirements/production.txt

- Go to the sub-folder containing the tool documentation::

    cd docs_src

- Re-create the tool documentation and place it in the appropriate folder::

    make clean html copy_to_docs

- Go back to the project folder::

    cd ..

- Collect all files to be served statically::

    python3 manage.py collectstatic

- Apply the migrations to the database::

    python3 manage.py migrate

- Check that the configuration is ready to run::

    python3 manage.py check --deploy

- Restart the ``supervisord`` configuration::

    supervisorctl -c ../supervisor.conf reload

- Flush the cache::

    redis-cli flushall

- Restart the apache web server and check the new version is properly
  installed.
