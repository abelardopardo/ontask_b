.. _upload_database:

Uploading Data from a Remote Database
*************************************

OnTask allows to upload or merge data into a workflow's table using a previously configured connection clickin in the button |fa-plus| *SQL Connection*.

.. figure:: /scaptures/dataops_datauploadmerge.png
   :align: center

This link will be active only if these connections have been previously configured by the system administrator. After selecting the option to upload from a database, the next page shows the available SQL connections.

.. figure:: /scaptures/dataops_SQL_available.png
   :align: center

Clickin in the name of the connection will show its configuration parameters. Clicking in the |fa-rocket| *Run* button will open a dialog to obtain the additional data (if needed) to open the connection and load the data in OnTask.

.. figure:: /scaptures/dataops_SQL_run.png
   :align: center

The rest of the steps are identical to those used to either :ref:`upload new data<data_upload>` or :ref:`merge data with the existing table <merging>`.
