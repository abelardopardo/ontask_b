# OnTask: Personalised feedback at scale

Welcome to OnTask, the platform offering teachers and educational designers
the capacity to use data to personalise the experience for the learners.

Learning is complex, highly situated, and requires interacting with peers,
instructors, resources, platforms, etc. This complexity can be alleaviated
providing learners with the right support actions. But this process becomes
increasingly complex when the number of learners grows. The more learners,
the more difficult is for instructors to provide support and the usual
solution is to provide generic resources that are only relevant to a subset
of the audience (think reminder about upcoming assessment deadline).

In parallel wih this increase in complexity, learning platforms now generate
a wealth of data about those interactions that are technology mediated. This
data can be collected and used to help instructors and designers to provide a
truly personalised experience. Why is this not hapenning in current
platforms? Because the connection between this data and learner support
actions is very challenging to implement. This is the focus of OnTask:
provide instructors and designers with a platform to connect data emerging
from learning environments with highly personalised student support actions.

Why OnTask? There are several platforms out there that implement similar
functionality, and the common thread is the positive impact that personalised
communication may have when supporting learners. There are a few scientific
publications that document the ideas and processes that inspired the creation
of OnTask:

- Liu, D. Y.-T., Taylor, C. E., Bridgeman, A. J., Bartimote-Aufflick, K., & Pardo, A. (2016). Empowering instructors through customizable collection and analyses of actionable information Workshop on Learning Analytics for Curriculum and Program Quality Improvement (pp. 3). Edinburgh, UK.
- Liu, D. Y. T., Bartimote-Aufflick, K., Pardo, A., & Bridgeman, A. J. (2017). Data-driven Personalization of Student Learning Support in Higher Education. In A. Peña-Ayala (Ed.), Learning analytics: Fundaments, applications, and trends: A view of the current state of the art: Springer.  doi:10.1007/978-3-319-52977-6_5
- Pardo, A., Jovanović, J., Dawson, S., Gašević, D., & Mirriahi, N. (In press). Using Learning Analytics to Scale the Provision of Personalised Feedback. British Journal of Educational Technology. doi:10.1111/bjet.12592

## Installation

OnTask is a Web application that manages data about learners to provide them
with personalised support. For this reason, it is recommended an installation
that observes a set of tight security restrictions. Some of these
restrictions lie within the scope of the tool, but some other are part of the
environment in which the application is installed. We strongly recommend to
install OnTask in a web server that uses TTL encryption (HTTPS) to serve all
the pages. The application requires exchanging with your browser sensitive
information about your session, so the information should be encrypted.

### Requirements

OnTask has been developed as a [Django](https://www.djangoproject.com/)
application. Django is a high-level, python-based web framework that supports
a rich set of functionalities typically required in applications like OnTask.
But as with many other applications, OnTask requires a set of additional
applications for its execution:

- Python 2.7.13 (or later)
- Django (version 1.11.3 or later)
- Additional django modules (included in the requirements/base.txt) file
- Redis (version 4.0.2 or later)
- PostgreSQL (version 9.5 or later)

Some of these requirements are (hopefully) properly handled by
Python through its package index application [pip](https://pypi.python
.org/pypi/pip).

### Installing the required tools

The following installation steps assume that you are deploying OnTask in a 
production web server capable of serving pages using the HTTPS protocol.

#### Install and Configure Redis

1. Download and install [redis](https://redis.io).

   Follow the instructions to configure it to be used by Django.

2. Test that it executes properly

#### Install and Configure PostgreSQL

1. Download and install [postgresql](https://www.postgresql.org).

2. Create the role `ontask` with the command `createuser`. The role
   should be able to create new databases but not new roles and you should
   define a password for the user (use `createuser --interactive -W`).

3. Adjust the access configuration in postgresql (usually in file
   `pg_hba.conf`) to allow the newly created user to access databases locally.

4. Create a new database with name `ontask` with the `createdb` command.

5. Use the client application `psql` to verify that the user has access to
   the newly created database and can create and delete a new table and run
   regular queries. Try to connect to the database with the following command:

   ```bash
   psql -h 127.0.0.1 -U ontask -W ontask
   ```

   If the client does not connect to the database, review your configuration
   options.

#### Install Python

In the following sections we assume that you can open a command line
interpreter and you can execute the python intepreter.

1. Install [python](https://www.python.org).

2. Verify that the python interpreter can run and has the right version (2.7)
   using the command line interpreter.

3. Install [pip](https://pip.pypa.io/en/stable/) (the package may be called
   `python-pip`). This tool will be used by both python and django to install
   numerous libraries that are required to execute OnTask.

#### Download, install and configure OnTask


1. Download or clone a copy of [OnTask](https://github.com/abelardopardo/ontask_b).

2. Using a command interpreter, go to the OnTask folder and locate a folder
   inside it with name `requirements`. Verify that the `requirements`
   folder contains the files `base.txt`, `production.txt` and
   `development.txt`. The first file contains a list of python modules that
   are required by OnTask. The second is a set of additional modules to run a
   *production* instance, and the third is a list if you intend to run a
   *development* instance.

3. If you plan to run a production instance of OnTask execute the command:

   ```bash
     pip install -r requirements/production.txt
   ```
   
   Alternatively, if you plan to run a development instance of OnTask then
   execute the commmand:

   ```bash
     pip install -r requirements/development.txt
   ```
   This command traverses a list of libraries and modules and installs them as
   part of the python libraries in the system. These modules include Django,
   Django Rest Framework, django braces, etc.

At this point you have the major modules in place. The next steps include the
configuration of the Django environment to run OnTask.

If you plan to install a production instance of OnTask, using a plain text
editor (nano, vim, emacs or similar) in a command line interpreter, open the
file `manage.py` in the `src` folder of the project. Modify line 14
replacing the value `"ontask.settings.development"` by
`"ontask.settings.production"`. Save and close the file.

Using the same plain text editor create a file with name `local.env`
in the folder `src/ontask/settings` with the following content (note there is
no space between variable names and the equal sign):

   ```bash
   DEBUG=True
   TIME_ZONE='[YOUR LOCAL PYTHON TIME ZONE]'
   # syntax: DATABASE_URL=postgres://username:password@127.0.0.1:5432/database
   DATABASE_URL=postgres://[PSQLUSERNAME]:[PSQLPWD]@127.0.0.1:5432/ontask
   SECRET_KEY=
   ```

4. If you want to run a production instance, in the first line of the file
   change the word *True* by *False* (disables debugging information)

5. Open a command interpreter and execute the following python command:

   ```bash
     python -c 'import tzlocal; print(tzlocal.get_localzone().zone)'

   ```

   Replace `[YOUR LOCAL PYTHON TIME ZONE]` in the `local.env` file by the
   description of your time zone produced by the previous command.

6. Modify the fourth line (starting with `DATABASE_URL=` and change the
   field `[PSQLUSERNAME]` with the name of the Postgresql user created in the
   previous step (the one that could access the ontask database and run
   queries). If you decided to use a different name for the database, adjust
   the last part of the line accordingly (replace *ontask* by the name of
   your database).

7. Open a command interpreter and execute the following python command:

   ```bash
     python -c 'import random; import string; print("".join([random.SystemRandom().choice(string.digits + string.ascii_letters + string.punctuation) for i in range(100)]))'
   ```

   Copy the long string produced as output and add it at the end of the last
   line of the file `local.env`. It should look something like (with
   different content after the equal sign):

   ```bash
     SECRET_KEY=4o93jf0572094jv...
   ```

8. Create a new folder with name `logs` in the OnTask top folder (next to
   the `requirements` folder). This folder **is different** from the folder
   with the same name in the `src` folder.

9. If at some point during the following steps you want to reset
   the content of the database, run the commands `dropdb` and `createdb`

10. Execute the following commands to prepare the database initialization:

   ```bash
     python manage.py makemigrations profiles accounts workflow dataops
     python manage.py makemigrations table action email_action logs
   ```

11. Execute the following command to create the database internal structure:

    ```bash
     python manage.py migrate
    ```

   A few messages should appear on the screen related to the initalizaton
   of the database.

12. Execute the following command to upload to the platform an initial user
   group:

    ```bash
     python manage.py loaddata ontask/initial_data.json
    ```

13. Go to the `src` folder and execute the command to create a superuser
   account in OnTask:

    ```bash
     python manage.py createsuperuser
    ```

   Remember the data that you enter in this step so that
   you use it when you enter OnTask with your browser.

14. Go to the folder `src` of the project and execute the following
   command to check the status of the platform::

    ```bash
     python manage.py check --deploy
    ```

   The command should print just one warning about the
   configuration variable `X_FRAME_OPTIONS`.

15. Execute the following command to start the OnTask server:

    ```bash
     python manage.py runserver
    ```

   If there are no errors, the message on the screen should say that your
   server is running and available in the URL `127.0.0.1:8000`

### The Administration Pages


As many applications developed using Django, OnTask takes full advantage of
the administration pages offered by the framework. The account created with
the command `createsuperuser` has complete access to those pages through a
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

### Production Deployment

Once OnTask is executing normally, you may configure a web server (nginx,
apache or similar) to make it available to a community of users. The
instructions to make such deployment are beyond the scope of this manual but
they are available for users to consult.

## Authentication

OnTask comes with two default authentication mechanisms: `REMOTE_USER` and
basic authentication. The [first method uses the variable REMOTE_USER](https://docs.djangoproject.com/en/1.11/howto/auth-remote-user/#authentication-using-remote-user) that is assumed to be defined by an external application. This
method is ideal for environments in which users are already authenticated and
are redirected to the OnTask pages (for example, using SAML). If OnTask
receives a request from a non-existent through this channel, it automatically
and transparently creates a new user in the platform with the user name
stored in the `REMOTE_USER` variable.

If such variable is not set in the environment, OnTask resorts to
conventional authentication requiring email and password. These credentials
are stored in the internal database managed by OnTask. With these two
mechanisms, you may have two communities of users, those that are
authenticated externally (and access the platform directly), and those that
are authenticaticated with the credentials stored in OnTask.

There are other possibilities to handle user authentication (LDAP, AD, etc.)
but they require ad-hoc customizations of the tool.

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## Credits

OnTask has been developed as part of the [OnTask Project](https://ontasklearning.org) titled *Scaling the Provision of Personalised Learning Support Actions to Large Student Cohorts* and supported by the Office for Leanring and Teaching of the Australian Government.

## License

MIT License

Copyright (c) 2017 Office for Learning and Teaching. Australian Government

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
