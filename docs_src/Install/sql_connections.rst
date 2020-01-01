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

