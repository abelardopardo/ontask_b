.. _table:

Table
*****

   "You're here because you know something. What you know you can't explain,
   but you feel it"
   -- Morpheus, The Matrix

The information stored in the workflow table is accessed through the |bi-table| *Table* link in the top bar menu selecting the option **View data**. As this table can be arbitrarily large, the application groups the rows into pages and provides links to each of the pages at the bottom of the table. The top of the table includes a pull down menu to choose how many rows are shown per page. If the table has a large number of columns, a horizontal scroll is available to show the additional content. The order of the columns in the table can be changed by dragging them from the top row and dropping them in a new position.

The following figure shows an example of the full table view page.

.. figure:: /scaptures/table.png
   :align: center
   :width: 100%

The table offers the possibility of searching for a string using the box at the top right corner.

.. include:: /Tutorial/Tasks/include_table_top_buttons.rst

.. _table_views:

Table Views
===========

Due to the potentially large size of the workflow table in either number of rows or columns, OnTask offers the possibility to define *Views*. A view is a subset of columns and rows of the original table. You may define as many views as needed. The link *Views* in the main table page shows the views available and the operations to manage them.

.. figure:: /scaptures/table_view_view.png
   :align: center
   :width: 100%

The title at the top of the page is the view's name. The buttons to the right of the name perform the following operations:

|bi-pencil-fill| Edit
  Edit the view: name, description, set of columns to show and row filter

|bi-files| Clone
  Create a duplicate of this view with the prefix *Copy_of* added to its name. This operation is useful to create a new view with content that is similar to an already existing one (clone and edit).

|bi-trash-fill| Delete
  Delete the view.

If the view has defined a filter condition (to select a subset of the rows), it is shown on top of the table.

When creating a view you need to provide a name (required), a description, a subset of columns to show (at least one of them must be a **key column**), and an expression to select a subset of rows. This expression is evaluated with the values of every row and if the result is *True*, the row is included in the view. The following figure shows an example of the information that is included in the definition of a view.

.. figure:: /scaptures/table_view_edit.png
   :align: center
   :width: 60%

When visualising the subset of data in a view, the button with text **Views** at the top offers the option to go back to the *Full Table*, create a new view, or select any of the existing ones.
