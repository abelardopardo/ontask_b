.. _install:

====================
Installation process
====================

OnTask is a Web application that manages data about learners to provide them
with personalised support. For this reason, it is recommended an installation
that observes a set of tight security restrictions. Some of these
restrictions lie within the scope of the tool, but some other are part of the
environment in which the application is installed. We strongly recommend to
install OnTask in a web server that uses TTL encryption (HTTPS) to serve all
the pages. The application requires exchanging with your browser sensitive
information about your session, so the information should be encrypted.

Requirements
------------

OnTask has been developed as a `Django <https://www.djangoproject.com/>`_
application. Django is a high-level, python-based web framework that supports
a rich set of functionalities typically required in applications like OnTask.
But as with many other applications, OnTask requires a set of additional
applications for its execution:

- Python 2.7.13 (or later)
- Django (version 1.11 or later)
- Additional django modules (included in the requirements/base.txt) file
- Redis (version 4.0 or later)
- PostgreSQL (version 9.5 or later)

Some of these requirements are (hopefully) properly handled by
Python through its package index application `pip <https://pypi.python
.org/pypi/pip>`__.


Installing the required tools
-----------------------------

The following installation steps assume that you are deploying OnTask in a
production web server capable of serving pages using the HTTPS protocol.

Install and Configure Redis
***************************

1. Download and install `redis <https://redis.io/>`_.

   Follow the instructions to configure it to be used by Django.

2. Test that it executes properly

For OnTask you only need executing in the machine. If you use the default
settings, there are not additional changes required in OnTask (the code is
alrady using this application internally).

Install and Configure PostgreSQL
********************************

1. Download and install `postgresql <https://www.postgresql.org/>`_.

#. Create the role ``ontask`` with the command ``createuser``. The role
   should be able to create new databases but not new roles and you should
   define a password for the user (use ``createuser --interactive -W``).

#. Adjust the access configuration in postgresql (usually in file
   ``pg_hba.conf``) to allow the newly created user to access databases locally.

#. Create a new database with name ``ontask`` with the ``createdb`` command.

#. Use the client application ``psql`` to verify that the user has access to
   the newly created database and can create and delete a new table and run
   regular queries. Try to connect to the database with the following command::

     psql -h 127.0.0.1 -U ontask -W ontask

   If the client does not connect to the database, review your configuration
   options.

Install Python
**************

In the following sections we assume that you can open a command line
interpreter and you can execute the python intepreter.

1. Install `python <https://www.python.org/>`_

#. Verify that the python interpreter can run and has the right version (2.7)
   using the command line interpreter.

#. Install `pip <https://pip.pypa.io/en/stable/>`__ (the package may be called
   ``python-pip``). This tool will be used by both python and django to install
   numerous libraries that are required to execute OnTask.

Download, install and configure OnTask
**************************************

1. Download or clone_actions a copy of `OnTask <https://github.com/abelardopardo/ontask_b>`_.

#. Using a command interpreter, go to the OnTask folder and locate a folder
   inside it with name ``requirements``. Verify that the ``requirements``
   folder contains the files ``base.txt``, ``production.txt`` and
   ``development.txt``. The first file contains a list of python modules that
   are required by OnTask. The second is a set of additional modules to run a
   *production* instance, and the third is a list if you intend to run a
   *development* instance.

#. If you plan to run a production instance of OnTask execute the command::

     pip install -r requirements/production.txt

   Alternatively, if you plan to run a development instance of OnTask then
   execute the commmand::

     pip install -r requirements/development.txt

   This command traverses a list of libraries and modules and installs them as
   part of the python libraries in the system. These modules include Django,
   Django Rest Framework, django braces, etc.

At this point you have the major modules in place. The next steps include the
configuration of the Django environment to run OnTask.

If you plan to install a production instance of OnTask, using a plain text
editor (nano, vim, emacs or similar) in a command line interpreter, open the
file ``manage.py`` in the ``src`` folder of the project. Modify line 14
replacing the value ``"ontask.settings.development"`` by
``"ontask.settings.production"``. Save and close the file.

Using the same plain text editor create a file with name ``local.env``
in the folder ``src/ontask/settings`` with the following content (note there is
no space between variable names and the equal sign)::

   TIME_ZONE='[YOUR LOCAL PYTHON TIME ZONE]'
   # syntax: DATABASE_URL=postgres://username:password@127.0.0.1:5432/database
   DATABASE_URL=postgres://[PSQLUSERNAME]:[PSQLPWD]@127.0.0.1:5432/ontask
   SECRET_KEY=
   LTI_OAUTH_CREDENTIALS=key1=secret1,key2=secret2

#. Open a command interpreter and execute the following python command::

     python -c 'import tzlocal; print(tzlocal.get_localzone().zone)'

   Replace ``[YOUR LOCAL PYTHON TIME ZONE]`` in the ``local.env`` file by the
   description of your time zone produced by the previous command.

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
   comma-sepparated list of pairs key=secret for LTI authentication. See the
   section  :ref:`authentication` for more details about this type of
   authentication.

#. Create a new folder with name ``logs`` in the OnTask top folder (next to
   the ``requirements`` folder). This folder **is different** from the folder
   with the same name in the ``src`` folder.

#. If at some point during the following steps you want to reset
   the content of the database, run the commands ``dropdb`` and ``createdb``

#. Execute the following commands from the ``src`` folder to prepare the
   database initialization::

     python manage.py makemigrations profiles accounts workflow dataops
     python manage.py makemigrations table action logs

#. Execute the following command to create the database internal structure::

     python manage.py migrate

   A few messages should appear on the screen related to the initalizaton
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
   server is running and available in the URL 127.0.0.1:8000

#. If OnTask is going to be accessed through a web server like Apache or Nginx,
   stop the application and configure the web server accordingly.

The Administration Pages
------------------------

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
---------------------

Once OnTask is executing normally, you may configure a web server (nginx,
apache or similar) to make it available to a community of users. The
instructions to make such deployment are beyond the scope of this manual but
they are available for users to consult.

.. _authentication:

Authentication
--------------

OnTask comes with three default authentication mechanisms (and are used in
the following order): LTI, ``REMOTE_USER``
and basic authentication.

- `IMS Learning Tools Interoperability (IMS-LTI) <http://www.imsglobal.org/activity/learning-tools-interoperability>`__.
  LTI is a standard developed by the IMS Global Leanring Consortium to
  integrate multiple tools within a learning environment. In LTI terms,
  OnTask is configured to behave as a *tool provider* and assumes a *tool
  consumer* such as a Learning Management System to invoke its functionality.
  Any URL in OnTask can be give nto the LTI consumer as the point of access.

  Ontask only provides two points of access for LTI requests coming from the
  consumer. One is the url with suffix ``/lti_entry`` and the second is the
  URL provided by the actions to serve the personalised content (accessible
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

- ``REMOTE_USER``.
  The second method uses `the variable REMOTE_USER <https://docs.djangoproject.com/en/1.11/howto/auth-remote-user/#authentication-using-remote-user>`__ that is
  assumed to be defined by an external application. This method is ideal for
  environments in which users are already authenticated and are redirected to
  the OnTask pages (for example, using SAML). If OnTask receives a request
  from a non-existent user through this channel, it automatically and
  transparently creates a new user in the platform with the user name stored
  in the ``REMOTE_USER`` variable. OnTask relies on emails as the username
  differentiator, so if you plan to use this authentication method make sure
  the value of ``REMOTE_USER`` is the email.

- Basic authentication.
  If the variable ``REMOTE_USER`` is not set in the internal environment of
  Django where the web requests are served, OnTask resorts to conventional
  authentication requiring email and password. These credentials
  are stored in the internal database managed by OnTask.

There are other possibilities to handle user authentication (LDAP, AD, etc.)
but they require ad-hoc customizations in the tool and are not provided as
out-of-the-box solutions.
