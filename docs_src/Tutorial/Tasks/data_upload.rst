.. _data_upload:

Data Upload
===========

Log into the platform and:

- Open an existing workflow without data, click in the button with name *Manage table data* and then in the *Data Upload/Merge* link, or

- Create a new workflow, introduce name and description.

The following page allows you to upload data from three sources: a CSV (comma separated values) file, an Excel file, or a SQL connection to a relational database.

.. figure:: ../../scaptures/dataops_datauploadmerge.png
   :align: center

You will upload the data included in the file :download:`student_list.csv <../../Dataset/student_list.csv>`. Download the file and store a copy in your computer. Click in the *CSV Upload/Merge* button. The next screen asks you to choose a file to upload the data. A CSV file is a text file in which the data is organized by lines, and the data in each line is separated by commas. A conventional spreadsheet program can save the data in this format. When uploading the file you can optionally specify a number of lines to skip at the top or bottom of your data file. This is useful when the CSV file is produced by another tool and contains some of these lines that have to be ignored.

.. figure:: ../../scaptures/dataops_csvupload.png
   :align: center

Choose the file :download:`student_list.csv <../../Dataset/student_list.csv>` and click in the *Next* button. The next screen shows the name of the columns detected in the file, the type (also automatically detected), a pre-filled field with the column name (in case you want to change it), and if it is a *key column* (there are no repeated values in all the rows).

.. figure:: ../../scaptures/tutorial_csv_upload_learner_information.png
   :align: center

The *key* columns are highlighted because a workflow must have at least one column of this type. Select all the column (clicking in the top element labeled *load*) and click on the *Finish* button. The data in the file has now been uploaded to the table that is part of the selected workflow.

