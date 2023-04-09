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

Password
  Password for the database. If not give, it will be required at execution time.

Host
  Host name or IP storing the remote database

Port
  Port to use to connect to the remote host

DB Name (required)
  Name of the remote database

Table
  Name of the table in the remote database containing the data to upload/merge. If not give, it will be requested at execution time.

Once a connection is defined, as described in :ref:`sql_connection_run`, all the data in the table will be accessed and loaded/merged into the current workflow.

The operations allowed for each connection are:

|bi-pencil-fill| Edit
  Change any of the parameters of the connection

|bi-eye-fill| View
  View the values of the connection

|bi-files| Clone
  Create a duplicate of the connection (useful to reuse configuration parameters)

|bi-trash-fill| Delete
  Remove the connection from the platform.

