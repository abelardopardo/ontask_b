.. _details:

Workflow Details
----------------

    "The details are not the details. They make the design"
    -- Charles Eames

After selecting a workflow to manage, the *details* page appears with a lot of information about operations, structure of the data, information about the columns, etc. The page contains the information shown in the following figure.

.. figure:: /scaptures/workflow_details.png
   :align: center

The name of the workflow is shown at the top of the page. The page includes links to additional menus with various operations on the selected workflow (some of them will be available depending on your user profile). Under the title *Workflow Details* there are buttons to access the following operations:

Add a column
  This menu opens three options: create a regular column, create a column combining the values of two existing columns, or create a new column with random values.

.. _details_add_column:

  Add a regular column
    Opens a dialog to create a new column in the table with the following fields:

    - Name (mandatory): column name (shown in the table)

    - Description: text that will be shown to the learners if the column is part of a survey action.

    - Data type (mandatory: The possible data types are *number* (representing both integers or real numbers), *string*, *boolean* (only possible values are *true* and *false*), and *datetime* (a date and time together).

    - An integer (mandatory) representing the position of the column in the table (a value zero will insert it at the end of the table).

    - Two date/time values to control the visibility of the column.

    - Comma-separated list of possible values. This field is to restrict the values in the column. The values have to be compatible with the specified data type.

    - Initial value to assign to all cells in the column.

    .. figure:: /scaptures/workflow_add_column.png
       :align: center

.. _details_add_formula_column:

  Add a formula-derived column
    This column is created by combining the values of existing columns using one of the operations addition, product, maximum, minimum, mean, median, standard deviation, conjunction or disjunction. The formula is only applied when the column is
    created the current values of the other columns. The column is not refreshed if the operand change in the future.

.. _details_add_random_column:

  Add a column with random values
    This is useful to create columns for A/B testing. The new column is created with a random value from either a numeric range (starting at 0) or a set of strings.

.. _details_attributes:

Attributes
  This is simply a dictionary of pairs ``(name, value)`` so that when a ``name`` appears in a personalized text, it is replaced by the ``value``. The main use of these attributes is when a value has to appear in various locations and you may want to change all its occurrences. For example, the instructor name could be included as one of the attributes so that if it changes, modifying the attribute is the only required step.

  .. figure:: /scaptures/workflow_attributes.png
     :align: center

.. _details_sharing:

Share
  A screen to make the workflow accessible to other users. You are supposed to know the user identification (there is no search functionality available).

  .. figure:: /scaptures/workflow_share.png
     :align: center

.. _details_export:

Export
  This functionality allows you to take a snapshot of the content of the workflow and store it in a file for your records. You may select which actions are included in the exported file

  .. figure:: /scaptures/workflow_export.png
     :align: center

  The menu offers the possibility of exporting only the data, or the data **and** the :ref:`action <action>` in the workflow.

.. _details_clone:

Clone
  This function creates a new workflow duplicating the data, actions and conditions of the current workflow. The new workflow will have the same name with the prefix *Copy of*.

.. _details_rename:

Rename
  This functionality allows to change either the name or the description of the workflow.

  .. figure:: /scaptures/workflow_rename.png
     :align: center

.. _details_flush_data:

Flush data
  This operation deletes all the data attached to the workflow, but preserves the workflow structure (that is, the name and the description only).

  .. figure:: /scaptures/workflow_flush.png
     :align: center

  Given the destructive nature of this operation the platform requires you to confirm this step.

.. _details_delete:

Delete
  Operation similar to the previous one, but now the whole workflow is deleted and therefore unselected. If executed, the platform will go back to the list of workflows as this one is no longer available for operations.

  .. figure:: /scaptures/workflow_delete.png
     :align: center

  As in the previous case, the platform asks for confirmation before carrying out the delete operation.

Under the buttons to carry out these workflow operations the platform shows a summary of the information contained in the workflow.

.. _columns:

The Columns
^^^^^^^^^^^

The data in a workflow is stored in a structure called *a table* that is made of rows and columns (similar to a spreadsheet). The details page basically shows information about the available columns.

.. figure:: /scaptures/wokflow_columns.png
   :align: center

Each column has a position, name (cannot contain the quotes *'* or *"*), a type (one of integer, string, double, boolean or date/time), a field stating if the values of that column are unique for the rows, and operations. When a column is marked as *Unique*, it means that all the values it contains are different and unique for each row. Think of a column containing a passport number. Such number is different for every person. There could be several columns with this property. The application detects automatically this property in a column. You may edit and change this properly as long as the values are the adequate ones (they satisfy the uniqueness property if you try mark a column as unique). The operations available over columns are:

Edit
  It allows you to change the name, type, unique and values allowed in the column. If you are changing the column type, the application will check if the existing values are valid. If not, the change will not be allowed.
  Similarly, if the *Unique* property is selected, the application checks the
  values to make sure this property is satisfied.

  .. figure:: /scaptures/workflow_column_edit.png
     :align: center

  The column may also have a *validity window* defined by two date/times. This validity is used when executing *action in* tasks.

Restrict
  Assigns as *allowed values* for the column those currently stored. This operation is useful to transform a generic column into one with values limited to the current ones.

Clone
  Clones the column in the workflow changing its name adding the prefix *Copy of* to the name.

Delete
  Deletes the column from the workflow. If there are conditions in the actions that use this column, those conditions will be removed from the action.

Statistics
  Shows a statistical summary of the values in the column. If the data type is *number*, the summary includes information about quartiles, a boxplot, and a histogram. For the rest of data types, the summary only includes the histogram.


