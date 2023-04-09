.. _details:

Workflow Operations
===================

    "The details are not the details. They make the design"
    -- Charles Eames

The *Workflow Operations* page is available through the *More* link at the top-bar menu. The page shows the information as illustrated by the following figure.

.. figure:: /scaptures/workflow_attributes.png
   :align: center

The buttons at the top of the page offer the following operations:

.. _details_export:

|bi-download| Export
  This functionality allows you to take a snapshot of the content of the workflow and store it in a file for your records. You may select which actions are included in the exported file

  .. figure:: /scaptures/workflow_export.png
     :align: center

  The menu offers the possibility of exporting only the data, or the data **and** the :ref:`action <action>` in the workflow.

.. _details_rename:

|bi-pencil-fill| Rename
  This functionality allows to change either the name or the description of the workflow.

  .. figure:: /scaptures/workflow_rename.png
     :align: center
     :width: 60%

.. _details_clone:

|bi-files| Clone
  This function creates a new workflow duplicating the data, actions and conditions of the current workflow. The new workflow will have the same name with the prefix *Copy of*.

.. _details_flush_data:

Flush data table
  This operation deletes all the data attached to the workflow, but preserves the workflow structure (that is, the name and the description only).

  .. figure:: /scaptures/workflow_flush.png
     :align: center
     :width: 60%

  Given the destructive nature of this operation the platform requires you to confirm this step.

.. _details_delete:

|bi-trash-fill| Delete
  Operation similar to the previous one, but now the whole workflow is deleted and therefore unselected. If executed, the platform will go back to the list of workflows as this one is no longer available for operations.

  .. figure:: /scaptures/workflow_delete.png
     :align: center
     :width: 60%

  As in the previous case, the platform asks for confirmation before carrying out the delete operation.

In addition to the buttons at the top, the *Workflow Operations* page offers two additional operations shown in separated tabs.


.. _details_attributes:

Attributes
  This tab shows the operations to manage a dictionary of pairs ``(name, value)``. The names can e used in personalized text and they are replaced by the ``value``.

  .. figure:: /scaptures/workflow_attributes.png
     :align: center

  The |bi-plus| *Attribute* button opens a form to introduce the name and value of a new attribute. The table below this button shows the attributes available for the workflow. The |bi-pencil-fill| icon opens the form to edit its content. The |bi-trash-fill| icon deletes the attribute.

  The use of these attributes is to facilitate a single point of change when a value appears in multiple locations. For example, every personalized text action is singed with the name of the instructor. If that name changes, all actions need to be edited. On the other hand, if the actions contain the name of an attribute, just changing the attribute value propagates the change to all actions.

.. _details_sharing:

Share
  The *Share* tab on the right of the page is used to manage the list of users that have access to this workflow. The |bi-plus| *User* button opens a form to introduce a the id of the user to share the workflow.

  .. figure:: /scaptures/workflow_share.png
     :align: center


.. _columns:

Column Operations
=================

The *Column Operations* page is available through the *More* link at the top-bar menu.  Columns in OnTask have substantial information and operations that is condensed in this page. The information is shown as illustrated by the following figure.

.. figure:: /scaptures/workflow_details.png
   :align: center

The buttons at the top of the page offer the following operations

|bi-plus| Column
  This menu opens three options: create a regular column, create a column combining the values of two existing columns, or create a new column with random values.

.. _details_add_column:

  Add a regular column
    Opens a dialog to create a new column in the table with the following fields:

    .. figure:: /scaptures/workflow_add_column.png
       :align: center
       :width: 60%

    - Name (mandatory): column name (shown in the table)

    - Description: text that will be shown to the learners if the column is part of a survey action.

    - Data type (mandatory: The possible data types are *number* (representing both integers or real numbers), *string*, *boolean* (only possible values are *true* and *false*), and *datetime* (a date and time together).

    - An integer (mandatory) representing the position of the column in the table (a value zero will insert it at the end of the table).

    - Two date/time values to control the visibility of the column.

    - Comma-separated list of possible values. This field is to restrict the values in the column. The values have to be compatible with the specified data type.

    - Initial value to assign to all cells in the column.

.. _details_add_formula_column:

  Add a formula-derived column
    This column is created by combining the values of existing columns using one of the operations addition, product, maximum, minimum, mean, median, standard deviation, conjunction or disjunction. The formula is only applied when the column is
    created the current values of the other columns. The column is not refreshed if the operand change in the future.

.. _details_add_random_column:

  Add a column with random values
    This is useful to create columns for A/B testing. The new column is created with a random value from either a numeric range (starting at 0) or a set of strings.

Below the buttons to perform these operations the workflow columns are shown. If the number of columns is large, the information is divided into pages. The field at the top right of this list performs searches in all fields of all columns (name, type, etc). Each column has the following information (from left to right):

Position (#)
  A number starting at 1. The position is used when :ref:`visualizing the table <table>`.

Operations
  The operations available for columns are:

  |bi-pencil-fill| Edit
    Change the name, description, unique and values allowed in the column. If the field *Has unique values per row* property is modified, OnTask checks if the values satisfy this condition.

    .. figure:: /scaptures/workflow_column_edit.png
       :align: center
       :width: 60%

    The column may also have a *validity window* defined by two date/times. This validity is used when executing *action in* tasks.

  |bi-files| Clone
    Clones the column in the workflow changing its name adding the prefix *Copy of* to the name.

  |bi-bar-chart-line-fill| Statistics (only for non-key columns)
    Shows a statistical summary of the values in the column. If the data type is *number*, the summary includes information about quartiles, a boxplot, and a histogram. For the rest of data types, the summary only includes the histogram.

  |bi-file-zip-fill| Restrict
    Assigns as *allowed values* for the column those currently stored. This operation is useful to transform a generic column into one with values limited to the current ones.

  |bi-trash-fill| Delete
    Deletes the column from the workflow. If there are conditions in the actions that use this column, those conditions will be removed from the action.

  |bi-skip-start-fill| Make first column
    Move this column to the first position in the workflow

  |bi-skip-end-fill| Make last column
    Move this column to the last position in the workflow

Name
  Unique name for the workflow that cannot contain the quotes *'* or *"* or start with *__*.

Description
  Description of the column.

Type
  One of integer, string, double, boolean or date/time.

Key?
  Field stating if it is a **key column**, that is, the values are different or unique for all rows. OnTask detects automatically this property when the data for a new column is loaded. You may edit and change this properly as long as the two requirements are satisfied: the values have to be unique for all rows, and there must be at least one key column per workflow.

The position of the columns can also be changed by dragging by the number (left-most column) and dropping them in the new position.
