.. _install:

Installation process
####################

OnTask is a Web application that manages data about learners to offer them personalized support. For this reason the installation process includes a set of tight security restrictions. Some of them lie within the scope of the tool, but others are part of the environment in which the application is installed. We strongly recommend to install OnTask in a web server that uses TTL encryption (HTTPS) to serve all the pages. The application requires exchanging sensitive information about your session with the browser, so the information should be encrypted.

Requirements
************

OnTask has been developed as a `Django <https://www.djangoproject.com/>`_ application. Django is a high-level, python-based web framework that supports a rich set of functionality typically required in applications like OnTask. As many other web applications, OnTask requires a set of additional libraries for its execution, namely:

- Python 3.7
- Django 2.2
- Additional Django modules listed in the file ``requirements/base.txt``
- Redis 
- PostgreSQL (version 9.5 or later)

Some of these requirements are handled using `pip <https://pypi.python.org/pypi/pip>`__ (Python's package index application).

If you are upgrading OnTask from a version lower than 2.8 to 2.8 or later, you need to disable the ``crontab`` used to execute tasks asynchronously from the web server. Starting in version 2.8 those tasks are executed by an application called ``celery`` that is managed using ``supervisor`` (see :ref:`scheduling_tasks`).

Are you upgrading from version < 4.0 to 4.2?
********************************************

The upgrade to 4.0 or later requires version 2.7 and 3.6 both installed and available in the system. Django versions 2.0 and later require Python 3 but certain additional libraries used by OnTask have not been fully ported yet and still require the use of Python 2.7. Make sure both versions are available before proceeding to the upgrade.

Are you upgrading from version < 4.3 to 4.3?
********************************************

The  upgrade to 4.3 or later no longer requires two versions of Python. It only requires Python 3. Make sure the application is only using version 3.

Are you upgrading to version 5.2?
*********************************

Version 5.2 contains a significant reorganization of the file structure in the tool, and as a consequence there are several files that need to be manually relocated:

- The :ref:`configuration file <configuration_file>` needs to be moved from ``src/ontask/settings`` to ``ontask/settings``.

- The the files in the ``media`` folder need to be moved to ``ontask/media``.

Required tools
**************

The following installation steps assume that you are deploying OnTask in a production web server capable of serving pages using the HTTPS protocol.

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

Install Python 3
================

In the following sections we assume that you can open a command line interpreter and you can execute the two python interpreter for version 3.

1. Install `python <https://www.python.org/>`_

#. Verify that the interpreter can run and has the right version (3) using the command line interpreter (either ``python --version`` or ``python3 --version``).

#. Install `pip <https://pip.pypa.io/en/stable/>`__ (the package may be called ``python3-pip`` for Python 3). This tool will be used to install additional libraries required to execute OnTask.

#. Some python libraries will require compiling source code, so make sure the package python3.7-dev is also installed.

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

  The configuration file contains a set of variable definitions that are fixed for the given platform. The values are written in a file and kept within the system file readable by the application (in the ``ontask/settings`` folder). This variables can store strings, booleans, basic lists and dictionaries.

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
  Python expression pointing to the configuration script or initial module (python file) to execute on start up. Two of these modules are provided in the folder ``ontask/settings``. The file ``development.py`` provides definitions recommended for a development environment. The file ``production.py`` provides the suggested definitions for a production deployment. Both scripts load the definitions in the module ``base.py``. These scripts contain configuration definitions described in :ref:`configuration_script`.

  Default: ``ontask.settings.production``

``DOMAIN_NAME``
  Host name used to serve the application.

  Default: ``localhost``

``ENV_FILENAME``
  Name for the configuration file. It must be in the folder ``ontask/settings``

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

Using a plain text editor create a file with name ``local.env`` in folder ``ontask/settings`` (or a file with the name assigned to the environment variable ``ENV_FILENAME`` as described in :ref:`configuration_environment`). Include in this file either:

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

The are some additional configuration variables that directly defined in the modules ``base.py``, ``development.py`` and ``production.py`` in the folder ``ontask/settings``. Modify the python code to perform additional configuration considering:

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

         os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          "ontask.settings.development")

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

.. _upgrading:

Upgrading OnTask
****************

If you have OnTask already configured and running, here are the steps to follow to upgrade to a new version:

- Create a backup of the database to be able to restore the state of the tool before the upgrade process.

- Stop the apache web server.

- Open a terminal and use a command interpreter to execute the following commands.

- Set the current folder of the interpreter to the main project folder.

- Verify that the :ref:`configuration file <configuration_file>` is in the folder ``ontask/settings``.

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

.. _admin_pages:

The Administration Pages
************************

OnTask uses the administration pages offered by Django. The account created with
the command ``createsuperuser`` has complete access to those pages through a
link in the upper right corner of the screen.

These pages offer access to several important operations:

- The elements of each of the models stored in the database (workflows,
  actions, conditions, columns, etc). Each model has its corresponding page
  allowing the creation, update and deletion of any object.

- The user information. This is a special model representing the users, their
  name, credentials, etc. The platform allows the creation of user accounts.

- The group information. The platform differentiates users based on groups.
  Each group has different functionalities.

Once the instance is running, visit these pages and configure the platform to
your needs.

.. _authentication:

Authentication
**************

OnTask comes with the following authentication mechanisms: IMS-LTI,
``REMOTE_USER`` variable, basic authentication, and LDAP. The first three
(IMS-LTI, ``REMOTE_USER`` and basic authentication) are enabled by default and used in that order whenever an unauthenticated request is received. It follows a brief description of how to configure them.

.. _ims_lti_config:

- `IMS Learning Tools Interoperability (IMS-LTI)
  <http://www.imsglobal.org/activity/learning-tools-interoperability>`__. LTI
  is a standard developed by the IMS Global Learning Consortium to integrate
  multiple tools within a learning environment. In LTI terms, OnTask is
  configured to behave as a *tool provider* and assumes a *tool consumer* such
  as a Learning Management System to invoke its functionality. Any URL in
  OnTask can be given to the LTI consumer as the point of access.

  Ontask only provides two points of access for LTI requests coming from the
  consumer. One is the URL with suffix ``/lti_entry`` and the second is the
  URL provided by the actions to serve the personalized content (accessible
  through the ``Actions`` menu.

  To allow LTI access you need:

  1) A tool consumer that can be configured to connect with OnTask. This type
     of configuration is beyond the scope of this manual.

  2) A set of pairs key,value in OnTask to be given to the tool consumers so that together with the URL, they are ready to send the requests. The key/value pairs need to be included as an additional variables in the file ``local.env`` in the folder ``ontask/settings`` together with other local configuration variables. For example, ::

       LTI_OAUTH_CREDENTIALS=key1=secret1,key2=secret2

  3) OnTask needs to identify those roles from the external tool mapped to the instructor role. This mapping is provided through a list of those roles in the following configuration variable::

       LTI_INSTRUCTOR_GROUP_ROLES=Instructor

  If you change the values of these variables, you need to restart the server so that the new values are in effect. This authentication has only basic functionality and it is assumed to be used only for learners (not for instructors).

- ``REMOTE_USER``. The second method uses `the variable REMOTE_USER
  <https://docs.djangoproject.com/en/2.1/howto/auth-remote-user/#authentication-using-remote-user>`__ that is assumed to be defined by an external application. This method is ideal for environments in which users are already authenticated and are redirected to the OnTask pages (for example, using SAML). If OnTask receives a request from a non-existent user through this channel, it automatically and transparently creates a new user in the platform with the user name stored in the ``REMOTE_USER`` variable. OnTask relies on emails to identify different user names, so if you plan to use this authentication method make sure the value of ``REMOTE_USER`` is the email.

  Additionally, this mode of authentication will be enforced in all requests reaching OnTask. However, this configuration prevents the recording of email reads. Read the section :ref:`email_config` to configure the server to allow such functionality to be properly configured.

- Basic authentication. If the variable ``REMOTE_USER`` is not set in the internal environment of Django where the web requests are served, OnTask resorts to conventional authentication requiring email and password. These credentials are stored in the internal database managed by OnTask.

The API can be accessed using through token authentication. The token can be generated manually through the user profile page. This type of authentication may need some special configuration in the web server (Apache or similar) so that the ``HTTP_AUTHORIZATION`` header is not removed.

.. _ldap_config:

LDAP Authentication
===================

OnTask may also be configured to use LDAP to authenticate users. This is done
through the external package `django-auth-ldap
<https://bitbucket.org/illocution/django-auth-ldap>`__. In its current version,
this authentication mode cannot be combined with the previous ones (this
requires some non-trivial code changes). The following instructions describe
the basic configuration to enable LDAP authentication. For more details check
the `documentation of the django-auth-ldap module
<https://django-auth-ldap.readthedocs.io/en/latest/>`__.

- Stop OnTask (if it is running)

- Make sure your server has installed the development files for OpenLDAP. In
  Debian/Ubuntu, the required packages are::

    libsasl2-dev python-dev libldap2-dev libssl-dev

  In RedHat/CentOS::

    python-devel openldap-devel

- Install the module ``django-auth-ldap``

- Edit the configuration file ``local.env`` and add the following two variable definitions::

    AUTH_LDAP_SERVER_URI=[uri pointing to your ldap server]
    AUTH_LDAP_PASSWORD=[Password to connect to the server]

- Edit the  file ``ontask/settings/base.py`` and uncomment the lines that import the ``ldap`` library (``import ldap``) and the lines that import three methods from the ``django_auth_ldap.config`` module (``LDAPSearch``, ``GroupOfNamesType`` and ``LDAPGroupQuery``)

- Locate the section in the file ``ontask/settings/base.py`` that contains the variables to configure *LDAP AUTHENTICATION*.

- Uncomment the ones needed for your configuration. Make sure all the information is included to connect to the server, perform the binding, search, and if needed, assign fields to user and group attributes.

- Locate the variable ``AUTHENTICATION_BACKENDS`` in the same file.

- Comment the lines referring to the back-ends ``LTIAuthBackend`` and
  ``RemoteUserBackend``.

- Uncomment the line referring to ``LDAPBackend``.

- Make sure the LDAP server contains the data about the users in the right
  format

- Start the OnTask server.

.. _email_config:

Email Configuration
*******************

OnTask relies on the functionality included in Django to send emails from the application. The following variables can be used in the configuration file:

``EMAIL_HOST``
  Host providing the SMTP service.

  Default: ``''``

``EMAIL_PORT``
  Port to communicate with the host

  Default: ``''``

``EMAIL_HOST_USER``
  User account to log into the email host

  Default: ``''``

``EMAIL_HOST_PASSWORD``
  Password for the account to log into the email host

  Default: ``''``

``EMAIL_USE_TLS``
  Boolean stating if the communication should use TLS

  Default: ``False``

``EMAIL_USE_SSL``
  Boolean stating if the communication should use SSL

  Default: ``False``

``EMAIL_ACTION_NOTIFICATION_SENDER``
  Address to use when sending notifications

  Default: ``''``

``EMAIL_HTML_ONLY``
  Send HTML text only, or alternatively, send text and HTML as an attachment

  Default: ``True`` (send HTML only)

``EMAIL_BURST``
  Number of consecutive emails to send before pausing (to adapt to potential throttling of the SMTP server)

  Default: ``0``

``EMAIL_BURST_PAUSE``
  Number of seconds to wait between bursts.

  Default: ``0``


An example of the content in the configuration is::

  EMAIL_HOST=smtp.yourinstitution.org
  EMAIL_PORT=334
  EMAIL_HOST_USER=mailmaster
  EMAIL_HOST_PASSWORD=somepassword
  EMAIL_USE_TLS=False
  EMAIL_USE_SSL=False
  EMAIL_ACTION_NOTIFICATION_SENDER=ontaskmaster@yourinstitution.org
  EMAIL_BURST=500
  EMAIL_BURST_PAUSE=43200


Set theses variables in the configuration file to the appropriate values
before starting the application. Make sure the server is running **in production mode**. The development mode is configured to **not send** emails but show their content in the console instead.

Tracking Email Reads
====================

If OnTask is deployed using SAML, all URLs are likely to be configured to go through the authentication layer. This configuration prevents OnTask from receiving the email read confirmations. In this case, the web server needs to be configured so that the SAML authentication is removed for the URL ``trck`` (the one receiving the email read tracking). In Apache, this can be achieved by the following directive::

  <Location /trck>
    Require all granted
  </Location>

If OnTask is not served from the root of your web server, make sure you include the absolute URL to ``trck``. For example, if OnTask is available through the URL ``my.server.com/somesuffix/ontask``, then the URL to use in the previous configuration is ``my.server.com/somesuffix/ontask/trck``.

.. _canvas_email_config:

Canvas Email Configuration
**************************

OnTask allows to send personalized emails to users's inbox in an instance of a `Canvas Learning Management System <https://www.canvaslms.com.au/>`_ using its API. Configuring this functionality requires permission from Canvas to access its API using OAuth2 authentication. Once this authorization is obtained, the following variables need to be defined in the file configuration file:

``CANVAS_INFO_DICT``
  A dictionary with elements pairs containing the identifier for a Canvas instance that will be shown to the user and a dictionary with the following configuration parameters:

  - ``domain_port``: A string containing the domain and port (if needed) of the Canvas host.

  - ``client_id``: This value is provided by the administrator of the Canvas instance once permission to use the API has been granted.

  - ``client_secret``: This value is provided together with the ``client_id`` once the permission to use the API is granted. It is typically a large random sequence of characters.

   - ``authorize_url``: URL template to access the first step of the authorization. This is usually ``https://{0}/login/oauth2/auth``. The string ``{0}`` is replaced internally with the value of ``domain_port``.

   - ``access_token_url``: URL template to access the token. This is usually ``https://{0}/login/oauth2/token``. The string ``{0}`` is replaced internally with the value of ``domain_port``.

  - ``conversation_URL``: Similar to the previous two values, it is the entry point in the API to create a conversation (equivalent to send an email). This is usually ``https://{0}/api/v1/conversations``. The string ``{0}`` is replaced internally with the value of ``domain_port``.

  - ``aux_params``: A dictionary with additional parameters. The dictionary may include a value for the key ``burst`` to limit the number of consecutive API invocations (to prevent throttling) and a value for the key ``pause`` with the number of seconds to separate bursts. Here is an example of the definition of this variable in the ``local.env`` file::

      CANVAS_INFO_DICT = {
          "Server one":
              {"domain_port": "yourcanvasdomain.edu",
               "client_id": "10000000000001",
               "client_secret": "YZnGjbkopt9MpSq2fujUO",
               "authorize_url": "http://{0}/login/oauth2/auth",
               "access_token_url": "http://{0}/login/oauth2/token",
               "conversation_url": "http://{0}/api/v1/conversations",
               "aux_params": {"burst": 10, "pause": 5}}
       }

  Default: ``{}`` (Empty dictionary)

``CANVAS_TOKEN_EXPIRY_SLACK``
  The number of seconds to renew a token before it expires. For example, if the variable is 300, any API call performed with a token five minutes before it expires will prompt a token refresh. Here is an example of such definition in ``local.env``::

      CANVAS_TOKEN_EXPIRY_SLACK=300

  Default: 600

After defining these variables, restart the application for the values to be considered. To test the configuration open a workflow, create an action of type ``Personalized canvas email`` and email those messages.

.. _plugin_install:

Plugins
*******

OnTask allows also the inclusion of arbitrary Python modules to execute and transform the data stored in a workflow. The Python code in the plugins is executed the same interpreter and execution environment as the rest of the platform. Thus, **use this functionality to execute only code that is fully trusted**. There is nothing preventing a plugin to run malicious code, so use at your own risk. To configure the execution of plugins follow these steps:

1. Create a folder at any location in your instance of OnTask to store the Python modules. OnTask assumes that each directory in that folder contains a Python module (that is, a folder with a file ``__init__.py`` inside).

#. Open the administration page of OnTask as superuser and go to the section with title `Data Upload/Merge Operations`.

#. Select the `Preferences` section.

#. Modify the field `Folder where plugins are installed` to contain the absolute path to the folder created in your systems.

#. Make sure that the Python interpreter that is currently executing the Django code is also capable of accessing and executing the code in the plugin folder.

#. Restart the server to make sure this variable is properly updated. 

#. To create a new plugin first create a folder in the plugin space previously configured. 

#. Inside this new folder create a Python file with name ``__init__.py``. The file has to have a structure a shown in :download:`the following template <__init__.py>`:

   .. literalinclude:: __init__.py
      :language: python

#. The menu *Dataops* at the top of the platform includes the page *Transform* that provides access to the plugins and its invocation with the current workflow.
 
 .. _sql_connections:

SQL Connections
***************

One of the key functionalities of OnTask is to be able to merge data from multiple sources. Section :ref:`dataops` describes the functionality available to perform these operations. Some of them, however, require special configuration from the tool administrator. This is the case when uploading and merging data from a remote database that allows SQL connections. These connections must be first defined by the administrator and are then are available to the instructors.

The screen to manage these connections is accessed clicking in the item *SQL Connections* at the top menu bar. This link is only available for those users with the administration role.

.. figure:: /scaptures/workflow_sql_connections_index.png
   :align: center

Each connection can be defined with the following parameters:

.. figure:: /scaptures/workflow_superuser_sql_edit.png
   :align: center

Name (required)
  Name of the connection for reference purposes within the platform. This name must be unique across the entire platform.

Description
  A paragraph or two explaining more detail about this connection.

Type (required)
  Type of database connection to be used. Typical types include *postgres*, *mysql*, etc.

Driver 
  Driver to be used for the connection. OnTask assumes that these drivers are properly installed and available to the underlying Python interpreter running Django.

User
  User name to connect to the remote database.

Requires password
  Flag denoting if the connection requires password. If it does, the password will be required at execution time. This feature allows OnTask to avoid storing DB passwords.

Host
  Host name or IP storing the remote database

Port
  Port to use to connect to the remote host 

DB Name (required)
  Name of the remote database

Table (required)
  Name of the table stored in the remote database and containing the data to upload/merge

Once a connection is defined, as described in :ref:`sql_connection_run`, all the data in the table will be accessed and loaded/merged into the current workflow.

The operations allowed for each connection are:

Edit
  Change any of the parameters of the connection

Clone
  Create a duplicate of the connection (useful to reuse configuration parameters)

Delete
  Remove the connection from the platform.

.. _bulk_user_creation:

Creating users in Bulk
**********************

OnTask offers the possibility of creating users in bulk through given the
data in a CSV file through the following steps:

1. Create a CSV file (plain text) with the initial line containing only the
   word ``email`` (name of the column). Include then one email address per
   user per line. You may check the file ``initial_learners.csv`` provided in
   the folder ``scripts``.

2. From the top level folder run the command::

     $ python3 manage.py initialize_db scripts/initial_learners.csv"

   If you have the user emails in a file with a different column name, you
   may provide the script that name (instead of the default ``email`` using
   the option ``-e``::

     $ python3 manage.py initialize_db -e your_email_column_name scripts/initial_learners.csv"

   If you want to create user accounts for instructors, you need to specify
   this with the option ``-i`` in the script::

     $ python3 manage.py initialize_db -e your_email_column_name -i scripts/initial_learners.csv"


Creating a Development Server using Docker
******************************************

You may use `Docker <https://docker.com>`_ to create a set of containers that run a **development** server. The file ``docker-compose.yml`` and the folder ``docker`` contains the configuration files to create the required images and instantiate them as containers. The current configuration creates the following containers:

OnTask Server
  Built on top of an ubuntu instance with Python 3, Django and Apache installed. The application is installed internally on port 80 in the container mapped to port 8080 of the local machine.

Message Queue
  Built on top of an ubuntu instance with Python 3, Django and an the OnTask source code. It executes a Celery daemon to receive execution requests.

Relational Database
  Built on top of the latest postgres docker image. It contains the database server with the data being stored in a separated volume (preserved among executions).

Redis
  Built on top of the latest redis docker image. It contains the cache server and broker for the message passing between Django and Celery.

The file ``docker-compose.yml`` contains the parameters to build the four containers and start the execution of OnTask.

After installing the Docker environment in your computer and creating the configuration file for the server running in the container, the sequence of commands to start the server is::

  docker-compose build
  docker-compose up

The process creates the containers and the server will be accessible through port 8080 in the host machine.
