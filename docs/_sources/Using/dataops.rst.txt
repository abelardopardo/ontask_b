.. _dataops:

Data Sources for Upload
=======================

    "May be stories are are just data without a soul"
    -- Brené Brown


This section describes the operations to upload and merge data into the table. It may be the case that this task is already done, or it is done automatically before you work with a workflow. If this is the case, you may skip this section. The data operations page offers various options to upload and merge data to the table and the process is divided into 2 to 4 steps.

CSV Files
---------

CSV or "comma separated value" files are plain text files in which the first line contains a comma-separated list of column names, and every subsequent line contains the values of these columns for each row. It is a popular format to exchange data that can be represented as a table, and it is for this reason that OnTask allows to upload data in this format.

The functionality assumes that you have such file available in your computer and provides a form to upload it to the platform. 

.. figure:: images/Ontask___CSVUpload.png
   :align: center

Some applications produce CSV files but the data is surrounded with by a few lines that need to be ignored. If this is the case, you may specify how many of these lines are present in your file and OnTask will ignored them when parsing the content.

Excel Files
-----------

The second format supported by OnTask to upload or merge data is Excel. 

.. figure:: images/Ontask___ExcelUpload.png
   :align: center 

In this case the file is assumed to have multiple *Sheets* and one of them has to be selected to upload/merge the data.

.. _sql_connection_run:

SQL connection
--------------

The third method to upload/merge data into the current workflow is through a SQL connection to a remote database. These connections have to be :ref:`previously defined and configured by the system administrator <sql_connections>`. Instructor users can use them to access the content of a previously defined table in a remote database. When selected, the option to upload data with  a SQL connection shows the table of available connections and the possibility to *Run* such connection:

.. figure:: images/Ontask___SQLAvailable.png
   :align: center

When *running* a SQL connection the platform shows the configuration parameters and request the password to access the remote database (if required). 

.. figure:: images/Ontask___SQLRun.png
   :align: center

Data Upload
===========

The operations described in the previous section obtain a data set and, if the workflow table is empty, it sets its initial content. In Step 2 of the process, OnTask offers the possibility of selecting and renaming the columns before they are uploaded to the table. For each column detected in the file, the table includes if it has been detected to be unique, its automatically detected type, a box to select, the name, and an alternative name (to allow column renaming). This step is to allow you to select those columns that are relevant and discard the rest. The platform requires you to choose **at least** one column with unique values.


.. figure:: images/OnTask____Upload_Merge_step2.png
   :align: center

After this step is performed, the data is stored in the table and the platform shows the :ref:`details` page. If these operations are done with a workflow that already has data in the table, then two additional steps are required as part of the *merge* operation.

Data Merge
==========

.. sidebar:: Merge a.k.a "Join"

   Merging is quite common in databases and is known as a *join* operation. There are several variants of join operations depending how the differences between the key columns are handled. These same variants exist when combining columns in data frames (or a table).

A merge operation is needed when you want to *merge* a set of columns with an **already existing table**. This operation is very common in data science contexts. One of the problems is to specify how the values in the columns are *matched* with respect to the ones already existing in the table. In other words, each new column has a set of values, but they need to be in the right order so that the information is matched appropriately for every row. The solution for this problem is to include in both the existing table and the new data being merged a **unique or key column**. These columns have the property that unique distinguish each row with a value and therefore they are used to make sure that rows with matching values in these columns are merged. When uploading new data in a workflow that already contains data in its table, the platform automatically detects it and executes two additional steps to complete a *merge* operation. 

The next step is the most delicate one. It requires you to identify the unique columns in both the existing data table and the one being uploaded, the criteria to merge the rows. We discuss each of these parameters in more detail.

.. figure:: images/Ontask____Merge2.png
   :align: center
   :width: 100%

Key columns
  You have to select a key column present in the data to be merged (mandatory) and a key column from the existing data (mandatory).

Merge method
  There are four types of merging. Once you choose an option an explanation appears below.

  Select only the rows with keys in both existing and new table
    It will process only the rows for which values in both key columns are present. Or in other words, any row for which there is no value in either of the key columns **will be dropped**.

    .. figure:: ../../src/media/merge_inner.png
       :align: center

  Select all rows in both the existing and new table
    All rows in both tables will be considered. You have to be careful with this option because it may produce columns that are no longer unique as a result.

    .. figure:: ../../src/media/merge_outer.png
       :align: center

  Select the rows with keys in the existing table
    Only the rows with a value in the existing table will be considered, the rest will be dropped.

    .. figure:: ../../src/media/merge_left.png
       :align: center

  Select the rows with keys in the new table
    Only the rows with a value in the table being uploaded will be considered, the rest will be dropped.

    .. figure:: ../../src/media/merge_right.png
       :align: center

In any of these variants, for those columns that are present in both the existing table and the new table, the values of the second will update the existing ones. This updating operation may introduce non-values in some of the columns. You have to take extra care when performing this operation as it may destroy part of the existing data. In the extreme case, if you try to merge a table with a key column with no values in common with the existing key and you select the method that considers rows with keys in both the existing and new table, the result is an empty table. 

After selecting these parameters the last step is to review the effect of the operation and proceed with the merge.

.. figure:: images/Ontask____Merge3.png
   :align: center

Plugins -- Transforming the data with your own code
===================================================

The additional method offered by OnTask to manipulate the data in a workflow's table is to execute arbitrary Python code encapsulated as a Python module and placed in a pre-defined folder in the computer hosting the server. In the context of the platform, these Python modules are called **Plugins** and require some :ref:`previous configuration <plugin_install>`. Before their execution, a plugin must be written and installed in the folder previously considered for that purpose.

The purpose of the plugins is to allow arbitrary transformations of the data attached to a workflow. The list of plugins available for execution can be accessed through the link *Transform* in the *Dataops* top menu item.

.. figure:: images/OnTask____Transform_list.png
   :align: center

Each plugin is shown with a (unique) name, a description, the last time the code was modified (based on the file modification time), if the plugin is ready to execute, and the link for either the *Run* operation, or a link to the diagnostics if the execution is not possible.

The plugin execution request shows a form to collect the parameters required for the operation.

.. figure:: images/OnTask____Run_Transformation.png
   :align: center

Input columns
  The columns from the data table that will be passed to the plugin. The plugin can define a set of *fixed* column names to extract. If this list is empty, the list is requested from the user.

Key column for merging
  The plugins are supposed to create additional columns, and they need to be merged with the existing data. For this procedure, a key-column is needed to make sure the rows of the newly created data are correctly stored. They key column from the current data frame is added as part of the input data frame passed to the plugin.

Output column names
  The plugins defines the names of the result columns. However, the upon execution, the user may rename any of those columns.

Suffix to add to the result columns
  This field is provided to do a one-place renaming. If given, this suffix is added to the names of all output columns.

Execution parameters
  This part of the form requests the pairs *(name, value)* as defined by the plugin.

After the appropriate data is provided the tool shows a plugin executing report showing the columns that will be created and how will they be merged with the existing data.

.. _plugin_requirements:

Plugin requirements
-------------------

The Python modules installed in the pre-defined folder need to satisfy various requirements to be considered for execution within OnTask. More precisely, the file ``__init__.py`` must contain:

1. Module variable ``class_name`` with the name of the class in the file that contains the required definitions.

1. Class field ``name`` with the plugin name to show to the users.

2. Class field ``escription_txt`` with a string with the detailed description of what the
   plugin does 

3. Class field ``input_column_names`` with a potentially empty list of column names 
(strings). If the list is empty, the columns are selected by the user at 
execution time.

4. Class field ``output_column_names`` with a non empty list of names (strings) of the 
columns to be used for the output of the transformation.

5. Class field ``parameters`` with an optionally empty list with tuples with the following
structure:

   ``('name', type, [list of allowed values], initial value, help_text)``


   These elements will be requested from the user before executing the
   plugin through a form. The conditions on these values are:

   - name must be a string
   - type must be a string equal to "integer", "double", "string", 
     "datetime" or "boolean". 
   - The list of values is to restrict the
     possible values
   - The initial value must be of the type specified by the second 
     element.
   - Help_text a string to show as help text

6. Class method ``run`` that receives:

   - a pandas data frame with the data to process

   - a string with the name of the key column that will be used to merge
     the result.
   - A dictionary of pairs (name, value) with the parameters described in
     the previous element.

   an d returns a result Pandas data frame. This frame **must** have one
   column with the key column name provided so that it can be properly
   merged with the existing data.

If a plugin does not comply with these properties the platform shows a summary of these checks to diagnose the problem.

.. figure:: images/OnTask____Plugin_diagnostics.png
   :align: center

