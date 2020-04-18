.. _docker_server:

Creating a Development Server using Docker
******************************************

You may use `Docker <https://docker.com>`__ to create a set of containers that run a **development** server. The file ``docker-compose.yml`` and the folder ``docker`` contains the configuration files to create the required images and instantiate them as containers. The current configuration creates the following containers:

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
