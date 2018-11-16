.. _workflow_details:

Workflow Details
================

Log into the platform and open a workflow that has data in the table. The details page shows the information about the columns as well as some additional operations for the workflow:

.. figure:: /scaptures/tutorial_details_1.png
   :align: center

The buttons at the top of the page are used to perform several operations over the workflow.

.. _tutorial_add_columns:

Adding columns
--------------

The left button in the area right below the title with name *Add Column*
allows you to add three types of columns:

:ref:`Add a new column <details_add_column>`
  This function allows you to manually add a new column to the data table. You need to provide the name, a description (optional), the type of data (one of string, number, datetime, or boolean), the position where this column is inserted in the workflow, a date/time window when the columns is visible, an optional comma-separated list of possible value (useful to restrict the values), and an optional initial value.

:ref:`Add a formula-based column <details_add_formula_column>`
  This function is to create a new column containing the result of the data from existing columns combined with certain basic operantions such as *maximum*, *minimum*, *sum*, *product*, *mean*, *median*, etc. The way it works is by selecting the operation and a subset of existing columns to use as operands.

:ref:`Add a column with random values <details_add_random_column>`
  This function creates a new column with values randomly taken from a pre-defined collection.

Uploading or Merging additional data
------------------------------------

The button labeled *Manage table data* allows to execute the operation to either :ref:`upload<data_upload>`/:ref:`merge<merging>` new data to the table, or to :ref:`execute an existing plugin<plugin_write>`.

Workflow operations
-------------------

The button with name *More workflow operations* offers the following
additional operations in the current workflow.

Workflow attributes
  You can define a set of *attributes* in the workflow. This is simply a set of
  pairs *name, value* that you can use to have a single place where a value is
  defined and then reused in several other locations. For example, the name
  of the course is probably going to appear in various communications with
  the learners. If you define the attribute *Course_name* with that value,
  you can then refer to the attribute and it will be replaced by its value.

Export workflow
  This functionality allows you to take all the information included in a
  workflow and export it. The functionality offers the option of including in
  the export only the data, or the data and the actions.

Rename workflow
  Use this function to change the name and description of the workflow.

Share workflow
  You may share a workflow with other instructors in the platform. The *Share*
  button will allow you to add/remove other users to this list. The other
  users will not be able to flush the data or delete the workflow. Whenever
  you open a workflow, it becomes unavailable for the other users with whom
  it is being shared until you either select another workflow or your session
  expires.

Clone workflow
  This button creates a clone of the workflow with the a name containing the
  prefix *Copy of*. Once the operation is executed, the workflow is
  available in the home screen (link in the upper left corner of the screen).

Flush Data
  This function deletes the data associated with the workflow. It maintains the
  set of attributes and the actions, but it removes the conditions and filters
  from all the actions.

Delete workflow
  This function deletes completely the workflow from the platform.


