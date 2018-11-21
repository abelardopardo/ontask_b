.. _the_dataset:

The Dataset
===========

OnTask relies on the existence of data about how learners interact in a given experience. This activity offers an *artificially generated* data set to explore the functionality in the platform.

Download and unpack the zip file :download:`dataset.zip </Dataset/dataset.zip>` in a folder in your personal computer. The folder should have the following files: ``student_list.csv``, ``midterm_results.csv``, ``forum_participation.csv``, ``blended_participation.csv`` and ``all_data.csv``. These files have been derived from the :ref:`previously described scenario<the_scenario>`.

This the information contained in each file:

File ``student_list.csv``
  A file with information about 500 students and the following column names:

  - Student id (SID),
  - Identifier (an auxiliary field),
  - email,
  - Surname,
  - GivenName,
  - MiddleInitial,
  - Full name,
  - Gender,
  - Course Code,
  - Program, with one of the values `FSCI`, `FEIT`, `FASS` or `SMED`,
  - Enrolment, with one of the values `HECS`, `Local` or `International`, and
  - Attendance with values either `Full Time` or `Part Time`.

File ``midterm_results.csv``
  File with information about 461 students with the following columns:

  - SID (with values identical to those in the previous file),
  - email,
  - Last Name,
  - First Name,
  - Columns `Q01` to `Q10` with the result of the 10 multiple choice questions (1 means correct, 0 means incorrect), and
  - the column `Total` with exam score (over 100 points).

File ``forum_participation.csv``
  File with information about 500 student and their participation in the discussion forum in the course. The columns in this file are:

  - SID (with values identical to those in the previous files),
  - The columns `Days online`, `Views`, `Contributions` and `Questions` replicated four times for weeks 2-5 with the week number as suffix for the column name, and
  - the accumulated values for `Days onine`, `Views`, `Contributions`, and `Questions` without any suffix.

File ``blended_participation.csv``
  File with information about learner engagement with the videos and questions complementing the videos for weeks 2 - 5 in the course. The columns in this file are:

  - SID (with values identical to those in the previous files),
  - Columns with names `Video_N_WM` contain the percentage of the video with number N in week M that has been visualized. For example `Video_2_W4` is the percentage of the second video in Week 4 that has been visualized.
  - Columns with names `Questions_N_WM` contain the percentage of questions from group N in Week M that have been answered. For example, `Questions_1_W4` is the percentage of questions in block 1 from Week 4 that have been answered.
  - Columns with names `Correct_N_WM` contain the percentage of questions from group N in Week M that have been correctly answered (and therefore a value smaller than the previous one).

File ``all_data.csv``
  This file is simply the union of all the columns from the previous files.

.. _key_columns:

Key columns
-----------

Each file in the dataset contains the data in *Comma Separated Values* or CSV. This format assumes that 1) the first line has the names of the columns separated by commas, and every line below that one contains the data for a row with the values also separated by commas. This format is used to store information with a structure similar to a table (rows and columns).

There is a special type of column that is of special interest in OnTask. If a column has a different value for each of the rows it is called a **key column**. The reason why these columns are important is because once one value is selected it unequivocally identifies one row in the table. For example, educational institutions typically assign an identifier (SID) to each student which is unique. If a table contains information about a set of students (one row, one student) and one column has the student ID, that column is then a **key column**. If during a procedure that is manipulating this table a student ID is given, that information uniquely identifies one row of that table.

.. _exploring_data_with_spreadsheet:

Exploring the data with a spreadsheet
-------------------------------------

Open the file ``student_list.csv`` with a recent version of Excel. Select all the data in the spreadsheet (you can use ``Crtl-A`` or ``Cmd-A`` in OSX) as shown in the following figure:

.. figure:: /scaptures/excel_select_data.png
  :align: center
  :width: 100%

Next click in the menu item `Insert` and then click in the `Table` icon as shown in the following figure.

.. figure:: /scaptures/excel_insert_table.png
  :align: center
  :width: 100%

If you see a dialogue showing you the range just selected and stating that the table has headers, just confirm the creation by clicking `OK`. You should now see the data in the spreadsheet with some colouring and a few icons in the cells at the top row as shown in the following figure.

.. figure:: /scaptures/excel_table.png
  :align: center
  :width: 100%

The cells in the top row are the names of the columns contained in the file. If you click in the triangle at the right of any cell you will see a menu as shown in the following figure:

.. figure:: /scaptures/excel_filter_menu.png
  :align: center

The menu allows you to sort the rows according to the value in the column (the buttons `Ascending` and `Descending`) and *filter* or select some of the rows to be viewed. In the example, the column contains four values that you can select individually. Click in the bottom part of the window to select/deselect values and verify that the content of the table changes (only a subset of rows is shown). You may view all rows by choosing the item `(Select All)`. Repeat this procedure with the columns with names `Program`, `Enrolment Type`, `Attendance`, `Gender` and `Course Code`. Once you select a value with the filter, type ``Crtl-up`` (``CMD-up`` in OSX) to move to the top of the table. Hold the Shift key and press ``Crtl-down`` (``Cmd-down`` in OSX) and the entire row should be selected. At the bottom of the Excel screen you will see the number of elements selected as a quick way to know the number of rows. Repeat the previous procedure and find out how many students are local, HECS or international.

Questions
---------

1. How many students are in your class?

#. How many `programs` do you have in the data? What is the break out of the students per program?

#. What type of enrolment do you have? What is the percentage of students for each value?

#. What is the gender balance in the course?