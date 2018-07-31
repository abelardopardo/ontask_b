.. _install:

********************
Installation process
********************

OnTask is a Web application that manages data about learners to provide them
with personalized support. For this reason, it is recommended an installation
that observes a set of tight security restrictions. Some of these
restrictions lie within the scope of the tool, but some other are part of the
environment in which the application is installed. We strongly recommend to
install OnTask in a web server that uses TTL encryption (HTTPS) to serve all
the pages. The application requires exchanging with your browser sensitive
information about your session, so the information should be encrypted.

Requirements
============

OnTask has been developed as a `Django <https://www.djangoproject.com/>`_
application. Django is a high-level, python-based web framework that supports
a rich set of functionalities typically required in applications like OnTask.
But as with many other applications, OnTask requires a set of additional
applications for its execution:

- Python 2.7
- Django 
- Additional Django modules (included in the requirements/base.txt) file
- Redis 
- PostgreSQL (version 9.5 or later)

Some of these requirements are handled through Python's package index application `pip <https://pypi.python.org/pypi/pip>`__.


Installing the required tools
=============================

The following installation steps assume that you are deploying OnTask in a production web server capable of serving pages using the HTTPS protocol.

Install and Configure Redis
---------------------------

Django requires Redis to execute as a daemon in the same machine to cache information about the sessions. No specific changes are required in the code, simply have the server running in the background.

1. Download and install `redis <https://redis.io/>`_.

   Follow the instructions to configure it to be used by Django.

2. Test that it is executing properly in the background (use the ``ping``
   command in the command line interface.

.. _install_postgresql:

Install and Configure PostgreSQL
--------------------------------

1. Download and install `postgresql <https://www.postgresql.org/>`_.

#. Create the role ``ontask`` with the command ``createuser``. The role
   should be able to create new databases but not new roles and you should
   define a password for the user (use ``createuser --interactive -W``).

#. Adjust the access configuration in postgresql (in the configuration file
   ``pg_hba.conf``) to allow the newly created user to access databases locally.

#. Create a new database with name ``ontask`` with the ``createdb`` command.

#. Use the client application ``psql`` to verify that the user has access
   the newly created database and can create and delete a new table and run
   regular queries. Test the connection with the following command::

     psql -h 127.0.0.1 -U ontask -W ontask

   If the client does not connect to the database, review your configuration
   options.

Install Python
--------------

In the following sections we assume that you can open a command line
interpreter and you can execute the python interpreter.

1. Install `python <https://www.python.org/>`_

#. Verify that the python interpreter can run and has the right version (2.7)
   using the command line interpreter.

#. Install `pip <https://pip.pypa.io/en/stable/>`__ (the package may be called
   ``python-pip``). This tool will be used by both Python and Django to install
   additional libraries required to execute OnTask.

Download, install and configure OnTask
--------------------------------------

1. Download or clone a copy of `OnTask <https://github.com/abelardopardo/ontask_b>`_.

#. Using a command interpreter, go to the OnTask folder and locate a folder
   inside it with name ``requirements``. Verify that it
   contains the files ``base.txt``, ``production.txt`` and
   ``development.txt``. The first file contains a list of python modules that
   are required by OnTask. The second is a set of additional modules to run a
   *production* instance, and the third is the same list if you intend to run a
   *development* instance.

#. If you plan to run a production instance of OnTask execute the command (you may need administrative privileges to execute this command)::

     pip install -r requirements/production.txt

   Alternatively, if you plan to run a development instance of OnTask,
   execute the command::

     pip install -r requirements/development.txt

   This command downloads  a set of libraries and modules and installs them as
   part of the python libraries in the system. 

At this point you have the major modules in place. The next steps include the configuration of the Django environment to run OnTask. If you plan to install a production instance of OnTask, using a plain text editor (nano, vim, Emacs or similar) in a command line interpreter, open the file ``manage.py`` in the ``src`` folder of the project. Modify line 10 replacing the value ``"ontask.settings.development"`` by ``"ontask.settings.production"``. Save and close the file.

Using the same plain text editor create a file with name ``local.env`` in the folder ``src/ontask/settings`` with the following content (note there is no space between variable names and the equal sign)::

   TIME_ZONE='[YOUR LOCAL PYTHON TIME ZONE]'
   BASE_URL=''
   DOMAIN_NAME='[YOUR DOMAIN NAME]'
   # syntax: DATABASE_URL=postgres://username:password@127.0.0.1:5432/database
   DATABASE_URL=postgres://[PSQLUSERNAME]:[PSQLPWD]@127.0.0.1:5432/ontask
   SECRET_KEY=
   LTI_OAUTH_CREDENTIALS=key1=secret1,key2=secret2

#. Open a command interpreter and execute the following python command::

     python -c 'import tzlocal; print(tzlocal.get_localzone().zone)'

   Replace ``[YOUR LOCAL PYTHON TIME ZONE]`` in the ``local.env`` file by the
   description of your time zone produced by the previous command.

#. If OnTask is going to be served from a location different from the root of your server (for example ``myhost.com/ontask``, then modify the value of the variable ``BASE_URL`` with the suffix that should follow the domain name (in the example, ``/ontask``).

#. Modify the line starting with ``DOMAIN_NAME=`` and change the field
``[YOUR DOMAIN NAME``] with the domain name of the machine hosting OnTask.

#. Modify the line starting with ``DATABASE_URL=`` and change the
   field ``[PSQLUSERNAME]`` with the name of the Postgresql user created in the
   previous step (the one that could access the ontask database and run
   queries). If you decided to use a different name for the database, adjust
   the last part of the line accordingly (replace *ontask* by the name of
   your database).

#. Open a command interpreter and execute the following python command::

     python -c 'import random; import string; print("".join([random.SystemRandom().choice(string.digits + string.ascii_letters + string.punctuation) for i in range(100)]))'

   Copy the long string produced as output and add it at the end of the last
   line of the file ``local.env``. It should look something like (with
   different content after the equal sign)::

     SECRET_KEY=4o93jf0572094jv...

#. Modify the line starting with ``LTI_OAUTH_CREDENTIALS`` and include a
   comma-separated list of pairs key=secret for LTI authentication. See the
   section  :ref:`authentication` for more details about this type of
   authentication.

#. Create a new folder with name ``logs`` in the OnTask top folder (next to the ``requirements`` folder). This folder **is different** from the folder with the same name in the ``src`` folder.

#. If at some point during the following steps you want to reset the content of the database, run the commands ``dropdb`` and ``createdb`` explained in :ref:`install_postgresql`.

#. Execute the following commands from the ``src`` folder to prepare the
   database initialization::

     python manage.py makemigrations profiles accounts workflow dataops
     python manage.py makemigrations table action logs scheduler table

#. Execute the following command to create the database internal structure::

     python manage.py migrate

   A few messages should appear on the screen related to the initialization
   of the database.

#. Execute the following command to upload to the platform some initial data
   structures::

     python manage.py runscript -v1 --traceback initial_data

   The command should run without any error or exception.

#. Execute the command to create a superuser
   account in OnTask::

     python manage.py createsuperuser

   Remember the data that you enter in this step so that
   you use it when you enter OnTask with your browser.

#. Go to the ``docs`` folder to generate the documentation. Make sure this
   folder contains the sub-folders with name ``_static`` and ``_templates``.
   Execute the command::

     make html

   The documentation is produced by the ``sphinx-doc`` application and
   generates the directory ``_build``. The documentation for the platform is in
   the folder ``_build/html``.

#. Copy the entire ``html`` folder (inside ``_build``) over to the
   ``src/static`` folder (in Unix ``cp -r _build/html ../src/static``).

#. From the ``src`` folder execute the following command to collect and install
   the static content::

     python manage.py collectstatic

#. If you are running a production instance, execute the following
   command to check the status of the platform::

     python manage.py check --deploy

   The command should print just one warning about the configuration variable
   X_FRAME_OPTIONS. If you are running a development instance, you will get
   various additional warning that are derived most of them from running the
   instance without HTTPS.

#. Execute the following command to start the OnTask server::

     python manage.py runserver

   If there are no errors, the message on the screen should say that your
   server is running in the url 127.0.0.1:800. However, if you open your
   browser in that URL, an error will be shown. This error is normal and it
   is because the production version requires the pages to be served through
   SSL with a valid certificate in a conventional server.

   If you want to use the server through the the URL 127.0.0.1:8000 you have
   to perform two more steps. First, edit the file ``manage.py`` and change
   these three lines to look like::

         os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          "ontask.settings.production")
         #                 "ontask.settings.development")

   Second, execute the following command from the ``src`` folder::

     pip install -r requirements/development.txt

   Now, the command::

     python manage.py runserver

   will start the server in the URL 127.0.0.1:8000 and you should be able to
   access it normally with the browser.

#. If OnTask is going to be accessed through a web server like Apache or Nginx,
   stop the application and configure the web server accordingly.

The Administration Pages
========================

As many applications developed using Django, OnTask takes full advantage of
the administration pages offered by the framework. The account created with
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

Production Deployment
=====================

Once OnTask is executing normally, you may configure a web server (nginx,
apache or similar) to make it available to a community of users. The
instructions to make such deployment are beyond the scope of this manual but
are available through the corresponding manual pages of these applications.

.. _authentication:

Authentication
==============

OnTask comes with the following authentication mechanisms: IMS-LTI,
``REMOTE_USER`` variable, basic authentication, and LDAP. The first three
(IMS-LTI, ``REMOTE_USER`` and basic authentication) are enabled by default and used in that order whenever an unauthenticated request is received. It follows a brief description of how to configure them.

- `IMS Learning Tools Interoperability (IMS-LTI)
  <http://www.imsglobal.org/activity/learning-tools-interoperability>`__. LTI
  is a standard developed by the IMS Global Learning Consortium to integrate
  multiple tools within a learning environment. In LTI terms, OnTask is
  configured to behave as a *tool provider* and assumes a *tool consumer* such
  as a Learning Management System to invoke its functionality. Any URL in
  OnTask can be give nto the LTI consumer as the point of access.

  Ontask only provides two points of access for LTI requests coming from the
  consumer. One is the URL with suffix ``/lti_entry`` and the second is the
  URL provided by the actions to serve the personalized content (accessible
  through the ``Actions`` menu.

  To allow LTI access you need:

  1) A tool consumer that can be configured to connect with OnTask. This type
     of configuration is beyond the scope of this manual.

  2) A set of pairs key,value in OnTask to be given to the tool consumers so
     that together with the URL, they are ready to send the requests. The
     key/value pairs are specified in the file ``local.env`` in the folder
     ``src/ontask/settings`` together with other local configuration variables.
     For example::

       LTI_OAUTH_CREDENTIALS=key1=secret1,key2=secret2

     If you change the values of this variable, you need to restart the server
     so that the new credentials are in effect.

  This authentication has only basic functionality and it is assumed to be
  used only for learners (not for instructors).

- ``REMOTE_USER``. The second method uses `the variable REMOTE_USER
  <https://docs.djangoproject.com/en/1.11/howto/auth-remote-user/#authentication-using-remote-user>`__
  that is assumed to be defined by an external application. This method is
  ideal for environments in which users are already authenticated and are
  redirected to the OnTask pages (for example, using SAML). If OnTask receives
  a request from a non-existent user through this channel, it automatically and
  transparently creates a new user in the platform with the user name stored in
  the ``REMOTE_USER`` variable. OnTask relies on emails as the user name
  differentiator, so if you plan to use this authentication method make sure
  the value of ``REMOTE_USER`` is the email.

  Additionally, this mode of authentication will be enforced in all requests reaching OnTask. However, this configuration prevents the recording of email reads. Read the section :ref:`email_config` to configure the server to allow such functionality to be properly configured.

- Basic authentication. If the variable ``REMOTE_USER`` is not set in the
  internal environment of Django where the web requests are served, OnTask
  resorts to conventional authentication requiring email and password. These
  credentials are stored in the internal database managed by OnTask.

The API can be accessed using through token authentication. The token can be
generated manually through the user profile page. This type of authentication
may need some special configuration in the web server (Apache or similar) so
that the ``HTTP_AUTHORIZATION`` header is not removed.

LDAP Authentication
-------------------

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

- Edit the configuration file ``local.env`` and define the following two
  variables::

    AUTH_LDAP_SERVER_URI=[uri pointing to your ldap server]
    AUTH_LDAP_PASSWORD=[Password to connect to the server]

- Edit the  file ``src/ontask/settings/base.py`` and uncomment the lines that
  import the ``ldap`` library (``import ldap``) and the lines that import three
  methods from the ``django_auth_ldap.config`` module (``LDAPSearch``,
  ``GroupOfNamesType`` and ``LDAPGroupQuery``)

- Locate the section in the file ``src/ontask/settings/base.py`` that contains
  the variables to configure *LDAP AUTHENTICATION*.

- Uncomment the ones needed for your configuration. Make sure all the
  information is included to connect to the server, perform the binding, search, and if needed, assign fields to user and group attributes.

- Locate the variable ``AUTHENTICATION_BACKENDS`` in the same file.

- Comment the lines referring to the back-ends ``LTIAuthBackend`` and
  ``RemoteUserBackend``.

- Uncomment the line referring to ``LDAPBackend``.

- Make sure the LDAP server contains the data about the users in the right
  format

- Start the OnTask server.

.. _email_config:

Email Configuration
===================

OnTask relies on the functionality included in Django to send emails from the
application. The configuration parameters are defined in the file ``base.py``
and are: ``EMAIL_HOST``, ``EMAIL_PORT``, ``EMAIL_HOST_USER``,
``EMAIL_HOST_PASSWORD``, ``EMAIL_USE_TLS`` and ``EMAIL_USE_SSL``.

Set theses variables in the configuration file to the appropriate values
before starting the application. Make sure the server is running **in production mode**. The development mode is configured to **not send** emails but show their content in the console instead.

Tracking Email Reads
--------------------

If OnTask is deployed using SAML, all URLs are likely to be configured to go through the authentication layer. This configuration prevents OnTask from receiving the email read confirmations. In this case, the web server needs to be configured so that the SAML authentication is removed for the url ``trck`` (the one receiving the email read tracking). In Apache, this can be achieved by the following directive::

  <Location /trck>
    Require all granted
  </Location>

If OnTask is not served from the root of your web server, make sure you include the absolute URL to ``trck``. For example, if OnTask is available through the URL ``my.server.com/somesuffix/ontask``, then the URL to use in the previous configuration is ``my.server.com/somesuffix/ontask/trck``.


.. _scheduling_tasks:

Scheduling tasks
================

OnTask allows to program certain tasks to execute at some point in the
future. This functionality is implemented using a combination of persistent
storage (the database), and a time-based job scheduler external to the tool.
Time-based job schedulers are present in most operating systems (``cron``
in Unix/Linux, or ``at`` in Windows). OnTask provides the functionality to
describe the task to execute and assign it a date and time. Additionally, the
tool has a script that checks the date/time, selects the appropriate task,
and executes it. These instructions describe the configuration assuming an
underlying Linux/Unix architecture using ``crontab``.

Create a *crontab* file for the user running the server in your production
environment with the following content::

  MAILTO="[ADMIN EMAIL ADDRESS]"
  PATH=/usr/local/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
  SHELL=/bin/bash
  ONTASK_PROJECT=[PATH TO ONTASK PROJECT ROOT]

  0,15,30,45 * * * * python ${ONTASK_PROJECT}/src/manage.py runscript scheduler_script -v3 --traceback --script-args="-d" > [CRONTAB LOG] 2>&1

Modify the previous script with the following information:

- In the first line change the email address by an address to receive the
  notifications produced by ``crontab``. The server running the application
  needs to have the capacity to send emails.

- Make sure the variable ``PATH`` contains the path to execute ``python``.

- Define the variable ``SHELL`` to point to the shell to use to execute
  ``python``.

- Change the value of the variable ``ONTASK_PROJECT`` to point to the root
  of OnTask (the folder containing the source code).

- In the last line replace ``[CRONTAB LOG]`` with a file to capture the
  output that the screen would write to a regular terminal. We recommend
  this file to be in a temporary directory.

The script ``scheduler_scrip`` has been configured to print messages through
a logger that writes the messages to the file ``script.log`` in the ``logs``
folder.

The remaining parameter to adjust is the frequency in which the script
``scheduler_script`` runs. In the example above, the script executes every 15
minutes (at minutes 0, 15, 30 and 45 minutes in the hour). Adjust this
frequency to suit your needs. Once adjusted, go to the administration menu in
OnTask, open the section with name *Core Configuration*, click in the
preferences and adjust the value of the *Minute interval to program scheduled
tasks* and match it (in minutes) to the interval reflected in the crontab.

.. _plugin_install:

Plugins
=======

OnTask allows also the inclusion of arbitrary Python modules to execute and transform the data stored in a workflow. The Python code in the plugins is executed the same interpreter and execution environment as the rest of the platform. Thus, **use this functionality to execute only code that is fully trusted**. There is nothing preventing a plugin to run malicious code (think ``system.exec('rm -rf /')``, so use at your own risk. To configure the execution of plugins follow these steps:

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
===============

One of the key functionalities of OnTask is to be able to merge data from multiple sources. Section :ref:`dataops` describes the functionality available to perform these operations. Some of them, however, require additional configuration from the administrator. This is the case for the uploading and merging of data from a remote database that allows SQL connections. These connections must be defined by the administrator and then they are available to the instructors.

The definition of these connections is done from the platform's home page, right after the table showing the available workflows.

.. figure:: ../Using/images/Ontask____SQLtable.png
   :align: center

Each connection can be defined with the following parameters:

.. figure:: ../Using/images/Ontask___SQLcreate.png
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

The operations allowed in each connection are:

Edit
  Change any of the parameters of the connection

Clone
  Create a duplicate of the connection (useful to reuse configuration parameters)

Delete
  Remove the connection from the platform.







