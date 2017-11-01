# OnTask: Personalised feedback at scale

OnTask connects data about learners with personalised support actions. Data 
is pervasive in some learning environments, but how can this data be used to 
improve the student experience? OnTask is an intuitive data management 
platform that allows you to use data about students to create personalised 
resources such as emails, set of resources, visualisations etc.

## Installation

OnTask uses the web development framework Django, Pandas (data management 
library), and a relational database (SQLite, MySQL or PostGreSQL). Although 
you can run the tool from a personal computer, the usual configuration is to 
install it as a web application in an institutional server. The following 
instructions describe the installation process for both the personal version,
and a corporate server with basic configuration.

### Install Python

[Python](https://www.python.org) is a programming language that is used
in a large number of applications. Its syntax (the way programs are written)
and libraries (code already available) make it a very powerful tool to process 
the data produced by servers (logs) and transform them into a more convenient 
format.

Visit the [Python download page](https://www.python.org/downloads/) and
follow the instructions to install the interpreter (the program that reads a
python program and executes it) in your computer. Make sure you test the
installation by executing the interpreter.

### PIP

As in the case of many programming languages, there are plenty of code
portions that have already been written in Python to perform the most common
tasks. These programs are packed and made available through a set of files 
that are called *libraries*. These libraries are what prevents programmers to 
take advantage of code written and made available by somebody else.

On of the applications that is used to handle Python libraries is [PIP](https://pip.pypa.io/en/latest/installing/). You execute PIP using a command interpreter 
window. 

### SQLite3 (recommended for installation in a personal computer)

Databases are typically applications that are created to handle a very large
amount of data and simultaneous operations (think of a database supporting the
information stored in a bank). Typically, these applications are not commonly 
stored in personal computers. [SQLite](https://www.sqlite.org/)
is a scaled down version of these applications that is useful to manage
small databases as if you were interacting with a larger database server. In
the context of this workshop we are going to use [SQLite](https://www.sqlite
.org/) to explore how data is stored and managed through a database, and how 
to process information contained in its tables.

You may directly create and manipulate a database using a command line
interpreter that is invoked with the text `sqlite3`. You will see that the 
prompt changes to `sqlite>`. You terminate the interpreter typing the
command exit. The command `.help` shows the rest of available commands. In 
principle, you will not need to use the interpreter. OnTask will create a set
 of tables on that database to store its inernal data.

### PostgreSQL (recommended for installation in a server)

[PostgresSQL](https://www.sqlite.org/) is one of the most advanced open 
source database applications. OnTask uses this application to store the 
data related to workflows, actions, etc.

After installing PosgreSQL you must:

* Configure PostgreSQL so that it can be accessed by OnTask within the same 
machine.
* Create a new database user
* Create a new database
* Test that the user under which the OnTask process will run can access and 
manipulate the new database.

### Requirements

Once you have installed the previous tools, go to the root folder in the 
project, open a command interpreter window and execute the command:
```bash
pip install -f requirements.txt
```
if you are installing OnTask for development, or 
```bash
pip install -f requirements/production.txt
```
if you are installing OnTask in a production environment (there are several 
apps that are ignored in this setting.)


## Usage

Once you have installed the server, go to the `src` folder and execute:
```bash
$ python manage.py migrate
$ python manage.py createsuperuser
```
answer the questions to create a user with maximum privileges to manage the 
appliction. Then, run
```bash
$ python manage.py runserver
```
and if your configuration is correct your server should be available through 
your browser.
 
## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## History

TODO: Write history

## Credits

TODO: Write credits

## License

TODO: Write license

