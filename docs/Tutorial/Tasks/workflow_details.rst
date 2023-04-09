.. _workflow_details:

Column operations
*****************

Log into the platform and open a workflow that has data in the table. Click in the *More* link in the top-bar menu. Select the option *Column operations*. The next page shows the information about the columns:

.. figure:: /scaptures/tutorial_details_1.png
   :align: center

The buttons at the top of the page are used to perform several operations over the workflow.

.. _tutorial_add_columns:

Adding columns
==============

The |bi-plus| *Column* button offers the following options:

Add a new column
  This function allows you to manually add a new column to the data table. You need to provide the name, a description (optional), the type of data (one of string, number, datetime, or boolean), the position where this column is inserted in the workflow, a date/time window when the columns is visible, an optional comma-separated list of possible value (useful to restrict the values), and an optional initial value.

Add a formula-based column
  This function is to create a new column containing the result of the data from existing columns combined with certain basic operations such as *maximum*, *minimum*, *sum*, *product*, *mean*, *median*, etc. The way it works is by selecting the operation and a subset of existing columns to use as operands.

Add a column with random values
  This function creates a new column with values randomly taken from a pre-defined collection.

