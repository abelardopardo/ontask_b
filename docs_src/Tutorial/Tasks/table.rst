.. _browsing_table:

Browsing the data table
=======================

Log into the platform and open a workflow that has data in the table. Click in the *Table* link at the top of the screen to see the stored data:

.. figure:: /scaptures/tutorial_initial_table.png
  :align: center

The buttons at the top of the page offer the following functions:

Add row
  It offers a page with a form to enter the data for a new row in the table.

Add column
  These operations are the ones discussed in the section s:ref:`tutorial_add_columns`.

Manage table data
  The operations to either upload/merge new data on the table, or transform its content executing pre-installed program in the platform (plugin).

Views
  This button allows you to manage (create, modify, delete) a set of :ref:`table views<tut_table_views>`, which show a subset of data in the table.

Dashboard
  This button shows a page summarizing the content in each of the columns in the table. The values are shown as a histogram. For the columns with numeric values, a boxplot, minimum, maximum, mean, standard deviation and quartiles is also shown.

CSV Download
  Allows to download a CSV file with the information currently shown in the
  screen.

.. _tut_table_views:

Table Views
-----------
For tables with a large number of columns and/or rows OnTask allows you to define a *view* of the table that shows only a subset of it. To create a view click first in the *Views* button at the top of the table page and then the *Add View* in the next page. Insert a name, description and select some of the columns as shown in the following figure.

.. figure:: /scaptures/tutorial_table_view_create.png
   :align: center

You can also define views to show only a subset of rows. The subset is selected using a *row filter* stating the conditions that must be satisfied by a row to be included in the view. These conditions are stated in terms of the column values.

Save the view and then click in the *View* button. The appropriate table subset is shown. The buttons at the top of the page allow you to edit the view (change the rows and columns selected), or select another available view.

.. figure:: /scaptures/tutorial_table_view.png
   :align: center

.. _tut_column_and_row_statistics:

Column and Row Statistics
-------------------------

If you click in the button with the column name in any of the table view and select the *Statistics*, OnTask shows a page with an statistical description of the values in that column. The analogous option is available through the *Operations* button in the row (left side of the table view). The page shows identical representations than in the case of the column stats, but for each column the words *Your value* appear in the location corresponding to the value in the row.

.. figure:: /scaptures/tutorial_row_statistics.png
   :align: center


