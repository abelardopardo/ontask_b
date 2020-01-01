.. _install:

Installation process
####################

OnTask is a Web application that manages data about learners to offer them personalized support. For this reason the installation process includes a set of tight security restrictions. Some of them lie within the scope of the tool, but others are part of the environment in which the application is installed. We strongly recommend to install OnTask in a web server that uses TTL encryption (HTTPS) to serve all the pages. The application requires exchanging sensitive information about your session with the browser, so the information should be encrypted.

.. toctree::
   :maxdepth: 2

   requirements
   install_ontask
   upgrade
   admin_pages
   authentication
   email_config
   canvas_email_config
   plugins
   sql_connections
   bulk_user_create
   docker_server
