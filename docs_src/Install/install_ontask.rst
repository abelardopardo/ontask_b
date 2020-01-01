.. _install_ontask:

Download, install and configure OnTask
**************************************

1. Download or clone a copy of `OnTask <https://github.com/abelardopardo/ontask_b>`_.

#. Using a command interpreter, go to the OnTask folder and locate a folder inside it with name ``requirements``. Verify that it contains the files ``base.txt``, ``production.txt`` and ``development.txt``. The first file contains a list of python modules that are required by OnTask. The second is a set of additional modules to run a *production* instance, and the third is the same list if you intend to run a *development* instance.

#. If you plan to run a production instance of OnTask execute the command::

     pip3 install -r requirements/production.txt

   You may need administrative privileges to execute this command.

   If you plan to run a development instance of OnTask, execute the command::

     pip3 install -r requirements/development.txt

   This command downloads  a set of libraries and modules and installs them as
   part of the python libraries in the system.

OnTask Configuration
====================

The next steps describe the configuration of the Django environment to run OnTask. This configuration is divided into in three groups of variables:

Environment variables (*env* level)

  These are variables defined by the operating system and available to OnTask upon execution. The values are obtained at the start of the deployment. Changing these variables usually requires re-deploying the platform (for example if you are using a container platform like docker). These variables can only store strings.

Configuration file (*conf* level)

  The configuration file contains a set of variable definitions that are fixed for the given platform. The values are written in a file and kept within the system file readable by the application (in the ``settings`` folder). This variables can store strings, booleans, basic lists and dictionaries.

Configuration script (*script* level)

  This is a python file that is read first by Django during its start-up procedure. The variables in this script can be defined using any python expression and may have arbitrarily complex expressions and operations (even function calls).

OnTask processes the variables in these context in the following stages:

1) The environment variables are loaded (if present)

2) The configuration file is loaded. If the file contains a definition for an environment variable, this is considered only if there is no value provided by the environment. In other words, an empty set of environment variables can be written in the configuration file and their values are considered. On the opposite side, if all environment variables are defined, any additional definition in the configuration file is ignored.

3) The initialization script is loaded with all the variables previously defined available.

.. _configuration_environment:

Environment variables
---------------------

The following variables, if defined in the environment, are considered by OnTask upon start.

``AWS_ACCESS_KEY_ID``
  Amazon Web Services access key id. This value is used when the static files in the server are served from a S3 bucket.

  Default: ``''``

``AWS_SECRET_ACCESS_KEY``
  Amazon Web Services secret attached to the given Access Key.

  Default: ``''``

``AWS_STORAGE_BUCKET_NAME``
  Name of the S3 Bucket used to serve the static content

  Default: ``''``

``AWS_LOCATION``
  Path within the AWS S3 Bucket where the static files are located

  Default: ``static``

``BASE_URL``
  Suffix that follows the host name when accessing OnTask once deployed. This is to allow OnTask to be deployed as part of a larger web server when the application is accessed as, for example, ``hostname.com/suffix/ontask``.

  Default: ``''``

``DATAOPS_MAX_UPLOAD_SIZE``
  Maximum file size for uploads

  Default: ``209715200`` (200 Mb)

``DATAOPS_PLUGIN_DIRECTORY``
  Folder in the local file system containing the OnTask plugins.

  Default: `plugins`

``DJANGO_SETTINGS_MODULE``
  Python expression pointing to the configuration script or initial module (python file) to execute on start up. Two of these modules are provided in the folder ``settings``. The file ``development.py`` provides definitions recommended for a development environment. The file ``production.py`` provides the suggested definitions for a production deployment. Both scripts load the definitions in the module ``base.py``. These scripts contain configuration definitions described in :ref:`configuration_script`.

  Default: ``settings.production``

``DOMAIN_NAME``
  Host name used to serve the application.

  Default: ``localhost``

``ENV_FILENAME``
  Name for the configuration file. It must be in the folder ``settings``

  Default: ``local.env``

``LANGUAGE_CODE``
  Official ISO 639-1 language code to use in the platform. Check the available languages in the file base.py.

  Default: ``en-us``

``LOG_FOLDER``
  Folder where to store the logs produced by the tool

  Default: ``logs`` folder at the root of the project

``MEDIA_LOCATION``
  URL suffix to be used by OnTask to access the media files in folder ``media``.

  Default: ``/media/``

``RDS_DB_NAME``, ``RDS_DB_USERNAME``, ``RDS_DB_PASSWORD``, ``RDS_DB_HOSTNAME``, ``RDS_DB_PORT``
  Parameters to access the platform database: database name, username, password, host name and port respectively.

  Default: All empty strings.

``SCHEDULER_MINUTE_STEP``
  Step in minutes to offer when scheduling action executions

  Default: ``15``

``SECRET_KEY`` **(Required)**
  Random string of characters used to generate internal hashes. It should be kept secret. If not defined the platform will raise an error upon start.

  Default: ``''``

``SESSION_CLEANUP_CRONTAB``
  Crontab string specifying the frequency to run the ``cleansessions`` command.

  Default `'05 5 6 * *'`

``STATIC_URL_SUFFIX``
  URL suffix to be used by OnTask to access the static files. This definition is ignored if ``AWS_ACCESS_KEY_ID`` is defined as it is assumed that the static content is served through AWS. Make sure this value is not terminated by a slash.

  Default: ``static``

``TIME_ZONE``
  String provided by the package ``pytz`` to identify the time zone in which the server is running. If you want to know the name of the time zone used by your platform execute the following command::

    python3 -c 'import tzlocal; print(tzlocal.get_localzone().zone)'

  Default: ``UTC``

Remember that if any of these variables is undefined in the execution environment, they still can be defined in the configuration file.

.. _configuration_file:

Configuration file
------------------

Using a plain text editor create a file with name ``local.env`` in folder ``settings`` (or a file with the name assigned to the environment variable ``ENV_FILENAME`` as described in :ref:`configuration_environment`). Include in this file either:

- the assignment of a variable from those described in :ref:`configuration_environment` that has no environment definition, or

- the assignment of any of the following variables for which you want a value different than the default.

The variables suitable to be included in the configuration file are:

``ALLOWED_HOSTS``
  Comma-separated list of host names used to validate the HTTP requests received by the platform. It helps to avoid processing requests that fake their Host headers. If OnTask is going to be hosted in ``www.yoursite.com``, then you may want to define it as ``www.yoursite.com,yoursite.com``. By default the platform allows request with any Host header.

  Default: ``[*]`` (any connection from any host)

``DATABASE_URL`` **(Required)**
  URL encoding the connection to the database. String of the format ``postgres://username:password@host:port/database``

``DEBUG``
  Flag to control if the execution is in DEBUG mode.

  Default: ``False``

``EXECUTE_ACTION_JSON_TRANSFER``
  Boolean stating if the JSON transfers should be executed when sending persnalized text.

  Default: ``False``

``REDIS_URL``
  List of URLs to access the cache service for OnTask. If there are several of these services, they can be specified as a comma-separated list such as ``'rediscache://master:6379,slave1:6379,slave2:6379/1'`` (see `Django Environ <https://github.com/joke2k/django-environ>`_)

  Default: ``rediscache:://localhost:6379??client_class=django_redis.client.DefaultClient&timeout=1000&key_prefix=ontask``

``SHOW_HOME_FOOTER_IMAGE``
  Boolean to control the appearance of a footer image in the home page. If true, the file ``footer_image.gif`` is shown from the media folder.

  Default: ``False``

``USE_SSL``
  Boolean to control if the server should use SSL for communication. There are several security features that are enabled with using SSL.

  Default: ``False``

There are additional variables to configure :ref:`Email <email_config>` and :ref:`Canvas Email <canvas_email_config>`.

Here is an example of a minimalistic configuration file (note there is no space between variable names and the equal signs)::

   ALLOWED_HOSTS=HOSTNAME1,HOSTNAME2
   BASE_URL=''
   # syntax: DATABASE_URL=postgres://username:password@127.0.0.1:5432/database
   DATABASE_URL=postgres://[PSQLUSERNAME]:[PSQLPWD]@127.0.0.1:5432/ontask
   DEBUG=False
   DOMAIN_NAME=[YOUR DOMAIN NAME]
   EXECUTE_ACTION_JSON_TRANSFER=True
   REDIS_URL=[YOUR REDIS URL]
   TIME_ZONE=[YOUR LOCAL PYTHON TIME ZONE]
   USE_SSL=True
   SECRET_KEY=[SEE BELOW]

1. Replace ``HOSTNAME1``, ``HOSTNAME2`` with a comma-separated list of hostnames of the platform hosting the tool.

#. If OnTask is going to be served from a location different from the root of your server (for example ``myhost.com/ontask``, then modify the value of the variable ``BASE_URL`` with the suffix that should follow the domain name (in the example, ``/ontask``).

#. Modify the line starting with ``DATABASE_URL=`` and change the
   field ``[PSQLUSERNAME]`` with the name of the Postgresql user created in the
   previous step (the one that could access the ontask database and run
   queries). If you decided to use a different name for the database, adjust
   the last part of the line accordingly (replace *ontask* by the name of
   your database).

#. Modify the line starting with ``DOMAIN_NAME=`` and change the field ``[YOUR DOMAIN NAME``] with the domain name of the machine hosting OnTask.

#. Replace the string ``[YOUR REDIS URL]`` with the URL where Redis can be
   accessed. This is typically something similar to
   ``redis://127.0.0.1:6379/1``.

#. Replace ``[YOUR LOCAL PYTHON TIME ZONE]`` with the description of your time zone (see the definition of the variable ``TIME_ZONE`` in :ref:`configuration_environment`.

#. Open a command interpreter and execute the following python command::

     python3 -c 'import random; import string; print("".join([random.SystemRandom().choice(string.digits + string.ascii_letters + string.punctuation) for i in range(100)]))'

   Copy the long string produced as output and add it at the end of the last
   line of the file ``local.env``. It should look something like (with
   different content after the equal sign)::

     SECRET_KEY=4o93jf0572094jv...

The configuration file may include additional variables to configure functionality such as :ref:`IMS LTI <ims_lti_config>`, :ref:`LDAP Authentication <ldap_config>`, :ref:`Email configuration <email_config>`, or :ref:`Canvas Email Configuration <canvas_email_config>`.

.. _configuration_script:

Configuration script
--------------------

The are some additional configuration variables that directly defined in the modules ``base.py``, ``development.py`` and ``production.py`` in the folder ``settings``. Modify the python code to perform additional configuration considering:

1) The script ``base.py`` is always executed first

2) The choice between ``develoment.py`` or ``production.py`` is decided based on the environment variable ``DJANGO_SETTINGS_MODULE`` and the default value is ``production.py``

.. _log_directory:

Log directory
-------------

Create a new folder with name ``logs`` in the OnTask top folder, next to the ``requirements`` folder, or in the location defined in the variable ``LOG_FOLDER``. This folder **is different** from the folder with the same name in the ``ontask`` folder.


OnTask Installation
===================

Once you have OnTask installed and configured and the tools Redis and Postgresql running, the next steps create the documentation, initial database configuration, additional site files, and deploy. To generate the documentation go to the folder ``docs_src``, make sure it contains the sub-folders with names ``_static`` and ``_templates`` and execute the command::

     make clean html copy_to_docs

The documentation is created by the application ``sphinx-doc`` and stored in the directory ``_build`` which is then copied to the ``../docs`` folder. Once the documentation has been created, the next steps configure the database. If at some point during the following steps you want to reset the content of the database, run the commands ``dropdb`` and ``createdb`` explained in :ref:`install_postgresql`. The following commands have to be execute from the project folder.

1. Execute the following command to create the database internal structure::

     python3 manage.py migrate

   A few messages should appear on the screen related to the initialization of the database.

#. Execute the following command to upload to the platform some initial data structures::

     python3 manage.py initialize_db

   The command should run without any error or exception. If you need to create additional users before deploying the platform, read the section :ref:`bulk_user_creation`.

#. Execute the command to create a superuser account in OnTask::

     python3 manage.py createsuperuser

   Remember the data that you enter in this step so that you use it when you enter OnTask with your browser.

#. Execute the following command to collect and install the static content::

     python3 manage.py collectstatic

   The static files are collected from the folder in the main project older with the name stored in the variable ``STATIC_URL_SUFFIX`` and placed, together with the static content from the folder ``ontask/static`` in the folder  ``<base_dir>/site/static``. This last folder is the only one that contains all the required files to be served statically by the application. Following the suggestions given in the Django project, the content in this folder should be served directly by the web server and not through the WSGI interface. The typical approach for this is to *synchronize* the content of this folder with the location from where the server takes the files. Make sure you do not make any changes to the folders ``<base_dir>/static`` or ``<base_dir>/ontask/static`` as they only contain a subset of the files.

#. If you are running a production instance, execute the following command to check the status of the platform::

     python3 manage.py check --deploy

   The command should print just one warning about the configuration variable
   X_FRAME_OPTIONS. If you are running a development instance, you will get
   various additional warning that are derived most of them from running the
   instance without HTTPS.

#. Execute the following command to start the OnTask server::

     python3 manage.py runserver

   If there are no errors, the message on the screen should say that your
   server is running in the url 127.0.0.1:8000. However, if you open your
   browser in that URL, an error will be shown. This error is normal and it
   is because the production version requires the pages to be served through
   SSL with a valid certificate in a conventional server.

#. If OnTask is going to be accessed through a web server like Apache or Nginx,
   stop the application and configure the web server accordingly.

#. If you want to use the server in development mode through the URL
   ``127.0.0.1:8000`` you have to perform two more steps. First, edit the file
   ``manage.py`` and change these three lines to look like::

         os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.development")

   Second, execute the following command from the project folder::

     pip3 install -r requirements/development.txt

   Now, the command::

     python3 manage.py runserver

   will start the server in the URL 127.0.0.1:8000 and you should be able to
   access it normally with the browser.

   .. admonition:: Warning

      The development version of OnTask is **not suited** to be used in
      production because it disables several security features. Make sure you
      only deploy a **production** version.

.. _scheduling_tasks:

Configure the Distributed Task Queue
====================================

There are various tasks that need to be executed by OnTask outside the web
server. The solution adopted is to use `Celery <http://www.celeryproject.org/>`_, `Supervisor <http://supervisord.org/>`_ (a process control system) and `Redis <https://redis.io/>`_. Redis has been configured in a previous step. This section explains how to set up the distributed task queue and make sure it is continuously executing in parallel with the web server.

1. Install the application ``supervisor`` using **pip3**::

     pip3 install supervisor

   This application makes sure the task queue program  Celery is continuously running in the background and in communication with the server.

2. Check that the binaries ``supervisord``, ``supervisorctl`` and ``celery``
   are installed in your system.

3. Go to the folder ``supervisor`` in the top of the project and edit the file
   ``supervisor.conf``.

4. The file configures ``supervisord`` to run in the background and prepare
   two sets of processes for OnTask. You have two options to use this file:

   a) Use environment variables.

      The file uses internally the value of two environment variables:

      * ``PROJECT_PATH``: Full path to the root of the project (the top
        folder containing the file ``LICENSE``.

      * ``CELERY_BIN``: Full path to the executable ``celery`` in your system
        (typically ``/usr/local/bin/celery`` or similar).

      * Set these variables in your environment to the correct values and make
        sure they are properly exported and visible when running other
        commands. For example, in ``bash``, this operation would be achieve
        by two commands similar to::

          $ export PROJECT_PATH=/full/path/to/OnTask/root/folder
          $ export CELERY_BIN=/full/path/to/celery/executable

   b) Change the file ``supervisor.conf``.

      * replace any appearance of the string ``%(ENV_PROJECT_PATH)s`` by the
        full path to the project folder.

      * replace any appearance of the string ``%(ENV_CELERY_BIN)s`` by the
        full path to the ``celery`` binary program.

4. Start the process control system with the command::

     $ supervisord -c supervisor.conf

   The command starts the process control application ``supervisord``
   which executes a set of process in the background.

5. Check that the process control system is working with the command
   (executed from the ``supervisor`` folder)::

     $ supervisorctl -c supervisor.conf status

   The output of this command should show a message similar to::

     ontask-beat-celery               RUNNING   pid 28579, uptime 1 day, 0:07:36
     ontask-celery                    RUNNING   pid 28578, uptime 1 day, 0:07:36

   If the status of the two processes is ``STARTING`` wait a few seconds and
   execute the command again. The names ``ontask-beat-celery`` and
   ``ontask-celery`` are the names of the two processes that OnTask uses for
   asynchronous task execution.

   You may use this command to check if ``supervisord`` is still running. The
   application is configured to write its messages to the file ``celery.log``
   in the logs folder at the top of the project.

6. If you are upgrading OnTask from a previous version (less than 2.8), you
   need to edit the ``crontab`` entry and remove the command to execute the
   script ``scheduler_script.py``.
