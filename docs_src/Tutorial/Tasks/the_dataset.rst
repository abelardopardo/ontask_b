.. _the_dataset:

The Dataset
***********

The following activities will use an *artificially generated* data set. Download and unpack the zip file :download:`dataset.zip </Dataset/dataset.zip>` in a folder in your personal computer. The folder should have the following files: ``student_list.csv``, ``midterm_results.csv``, ``forum_participation.csv``, ``blended_participation.csv`` and ``all_data.csv``. These files have been derived from the :ref:`previously described scenario<the_scenario>`.

This the information contained in each file:

File ``student_list.csv``
  A file with information about 500 students and the following column names:

  - **SID** (Student ID)
  - **Identifier** (an auxiliary field),
  - **email**,
  - **Surname**,
  - **GivenName**,
  - **MiddleInitial**,
  - **Full name**,
  - **Gender**,
  - **Course Code**,
  - **Program**, with one of the values `FSCI`, `FEIT`, `FASS` or `SMED`,
  - **Enrollment Type**, with one of the values `HECS`, `Local` or `International`, and
  - **Attendance** with values either `Full Time` or `Part Time`.

File ``midterm_results.csv``
  File with information about 461 students with the following columns:

  - **SID** (with values identical to those in the previous file),
  - **email**,
  - **Last Name**,
  - **First Name**,
  - Columns **Q01** to **Q10** with the result of the 10 multiple choice questions (1 means correct, 0 means incorrect), and
  - the column **Total** with exam score (over 100 points).

File ``forum_participation.csv``
  File with information about 500 student and their participation in the discussion forum in the course. The columns in this file are:

  - **SID** (with values identical to those in the previous files),
  - The columns **Days online**, **Views**, **Contributions** and **Questions** replicated four times for weeks 2-5 with the week number as suffix for the column name, and
  - the accumulated values for **Days online**, **Views**, **Contributions**, and **Questions** without any suffix.

File ``blended_participation.csv``
  File with information about learner engagement with the videos and questions complementing the videos for weeks 2 - 5 in the course. The columns in this file are:

  - SID (with values identical to those in the previous files),

  - Columns with names `Video_N_WM` contain the percentage of the video with number N in week M that has been visualized. For example `Video_2_W4` is the percentage of the second video in Week 4 that has been visualized.

  - Columns with names `Questions_N_WM` contain the number of questions from group N in Week M that have been answered. There are five questions per block.

  - Columns with names `Correct_N_WM` contain the number of questions from group N in Week M that have been correctly answered.

File ``all_data.csv``
  This file is simply the union of all the columns from the previous files.

.. _key_columns:

The format of all data files is *Comma Separated Values* or CSV. This format assumes that 1) the first line has the names of the columns separated by commas, and every line below that one contains the data for a row with the values also separated by commas. This format is used to store information with a structure similar to a table (rows and columns).

Key columns
===========

There are certain columns that are of special interest. If a column has a different value for each of the rows it is called a **key column**. The reason why are important is because once one value is selected it unequivocally identifies one row in the table. For example, educational institutions typically assign a unique identifier (SID) to each student. If a table contains information about a set of students (one student per row) and one column has the student ID, that column is then a **key column**.
