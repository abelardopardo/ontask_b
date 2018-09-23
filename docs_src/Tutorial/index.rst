.. _tutorial:

Tutorial
********

Before you start the tutorial make sure you have an instructor account in an
OnTask server. Also, download and unpack the zip file :download:`dataset.zip
<../Dataset/dataset.zip>` that contains a synthetic data set
with the following files: ``student_list.csv``, ``midterm_results.csv``,
``forum_participation.csv``, ``blended_participation.csv`` and ``all_data.csv``.
The data has been extracted from the hypothetical scenario shown in the
following figure.

.. figure:: the_dataset.png
   :width: 100%
   :align: center

We assume that a learning experience is through its sixth week. From weeks 2
to 5 learners were engaging with two videos and to set of questions per week.
In Week 6 students took a midterm examination consisting of 10 questions
(about 5 topics, 2 question per topic). Additionally, during these six weeks
a discussion forum has been available for them to make comments. The
information contained in each file is:

``student_list.csv``
  File with student id (SID), email, name, gender, course id (`UOS Code`),
  Degree (`FSCI`, `FEIT`, `FASS` or `SMED`), type of enrolment (`HECS`,
  `Local` or `International`) and attendance (Full Time or Part Time).

``midterm_results.csv``
  File with student id (SID), email, name, the result of the 10 multiple
  choice questions (1 means correct, 0 means incorrect) and the total exam
  score (0-100).

``forum_participation.csv``
  File with student id (SID), days online, views, contributions and questions
  for weeks 2-5, and the accumulated value for all weeks.

``blended_participation.csv``
  File with student id (SID), Video, questions answered, and questions
  answered correctly (for two items) for weeks 2-5.

``all_data.csv``
  All data from the previous files properly combined into a single file.

Remember the three central concepts in OnTask:

Workflow
  A container with the data (table), a set of procedures to manipulate
  columns, data upload and a set of actions. This entity is typically
  associated with a course, but it could also model an entire degree.

Table
  A two-dimensional structure in which each row represents a learner, and
  each column a learner attribute such as the score in an assessment, class
  attendance, number of interventions in the discussion forum, engagement with
  videos, etc.

Actions
  An action in OnTask can be one of two entities:

  * A HTML resource of which certain parts are included or excluded based on
    a set of **conditions** created with the learner attributes (for example,
    number of interventions in the forum is larger than five, and number of
    times a video was watched is larger than 2).

  * A set of questions that are shown to the students and their answers are
    incorporated to the data table.

The following figure represents the high level view of the tool.

.. figure:: drawing.png
   :align: center

The next sections explain how to perform various operations in OnTask.

.. _create_workflow:

Create a workflow
=================

Log into the tool and click in the tool icon on the top left corner of the
screen. If you have an instructor account, you will see the buNew tton to
create a new workflow as shown in the following figure.

.. figure:: ../scaptures/workflow_index_empty.png
   :align: center

The icon in the top right corner next to your profile image is a link to the
OnTask documentation. Click in the button to create a new workflow and enter
its name and a description.

.. figure:: ../scaptures/workflow_create.png
   :align: center

After creating the workflow opens it and shows the screen to
upload data to the table. The current workflow is shown underneath the top
menu as shown in the following figure (the string *BIOL1011* with a blue
background).

.. figure:: ../scaptures/dataops_datauploadmerge.png
   :align: center

You can always click in the *Workflows* item at the top menu to go back to
the home page and select a different workflow to open (or create a new one).

.. figure:: ../scaptures/workflow_index.png

From the home page you can also perform some additional operations in the
worklow such as :ref:`rename and change the workflow
description<details_rename>`, :ref:`cloning (or creating and
exact replica of this workflow with another name)<details_clone>`,
:ref:`delete all data in the workflow table<details_flush_data>`, or
:ref:`delete the workflow<details_delete>`.

Open a workflow
---------------

When you open a workflow, a page with its details is shown like the one in
the following figure

.. figure:: ../scaptures/workflow_details_empty.png
   :align: center

In this case the page only shows basic details because the workflow does not
have any data stored in its table. While the workflow is open, the top menu
contains the following links:

Details
  Is the current page that shows information about the columns, data types,
  number of actions, etc. contained in the workflow (empty now because we
  haven't populated it)

Table
  Operations to visualize and manipulate the table (search for values, add a
  row, add a column)

Actions
  Create, edit and execute actions.

Logs
  A table showing the history of operations performed on this workflow

In the current *Details* page, immediately under the title there are buttons
to perform the following operations:

- Manage table data

  - :ref:`Upload or merge data to the table <data_upload>`

  - :ref:`Run a plugin to transform the data in the table <plugin_run>`

- Workflow operations:

  - :ref:`Edit the attributes <details_attributes>`

  - :ref:`Export the workflow <details_export>`

  - :ref:`Rename or change the workflow description <details_rename>`

  - :ref:`Share the workflow with other users in the platform <details_sharing>`

  - :ref:`Clone the workflow <details_clone>`

  - :ref:`Flush the data in the table <details_flush_data>`

  - :ref:`Delete the workflow <details_delete>`

.. _data_upload:

Data Upload
===========

We now will upload the data included in the file
:download:`student_list.csv <../Dataset/student_list.csv>`.
From the page showing the *Details* of the workflow, click in the *Manage
table data* button and select the option *Upload or merge data*:

.. figure:: ../scaptures/dataops_datauploadmerge.png
   :align: center

Click in the *CSV Upload/Merge* button. The next screen asks you to choose a
file to upload the data. A CSV file is a text file in which the data is
organized by lines, and the data in the lines are separated by commas. A
conventional spreadsheet program can save the data in this format. When
uploading the file you can optionally specify a number of lines to skip at
the top or bottom of your data file. This is useful when the CSV file is
produced by another tool and contains some of these lines that have to be
ignored.

.. figure:: ../scaptures/dataops_csvupload.png
   :align: center

Choose the file :download:`student_list.csv
<../Dataset/student_list.csv>` and proceed to the next step. The next
screen shows the name of the columns detected in the file, the type (also
automatically detected), a pre-filled field with the column name (in case you
want to change it), and if it is a *key column* (there are no repeated
values in all the rows).

.. figure:: ../scaptures/tutorial_csv_upload_learner_information.png
   :align: center

The *key* columns are highlighted because a workflow must have at least one
column of this type. Select all the column (clicking in the top
element labeled *load*) and click on the *Finish* button.

Workflow Details
================

The details page now shows the information about the columns as well as some
additional operations for the workflow.
You can now see the information about the columns present in the workflow as
shown in the following figure:

.. figure:: ../scaptures/tutorial_details_1.png
   :align: center

.. _tutorial_add_columns:

Adding columns
--------------

The left button in the area right below the title with name *Add Column*
allows you to perform the following three operation.

:ref:`Add a new column <details_add_column>`
  Use this function to add a new column to the data table manualy (as opposed
  to the ones that were automatically derived from the CSV file you uploaded.

:ref:`Add a formula-based column <details_add_formula_column>`
  This function is to create a new column containing the result of the data
  from existing columns combined with certain basic operands.

:ref:`Add a column with random values <details_add_random_column>`
  This function is to populate a new column with values randomly taken from a
   pre-defined collection.

Uploading or Merging additional data
------------------------------------

The button labeled *Manage table data* allows to execute the operation to
upload/merge new data to the table, or to execute an existing plugin.

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

Browsing the table
==================

Once the data has been uploaded, click in the *Table* link at the top of the
screen to see the stored data:

.. figure:: ../scaptures/tutorial_initial_table.png
  :align: center

The buttons at the top of the page offer the following functionaity:

Add row
  It offers a page with a form to enter the data for a new row in the table.

Add column
  These operations are the ones discussed in the section
  :ref:`tutorial_add_columns`.

Manage table data
  The operations to either upload/merge new data on the table, or transform
  its content executing pre-installed program in the platform (plugin).

Dashboard
  This button leads to a page summarizing the content in each of the columns
  in the table. The values are shown as a histogram. For the columns with
  numeric values, a boxplot, minmum, maximum, mean, standard deviation and
  quartiles is also shown.

CSV Download
  Allows to download a CSV file with the information currently shown in the
  screen.

Table Views
-----------
For tables with a large number of columns and/or rows OnTask allows you to
define a *view* of the table that shows only a subset of it. To create a view
click first in the *Views* button at the top of the page and then the *Add
View* in the next page. Insert a name, description and select some of the
columns a shown in the following figure.

.. figure:: ../scaptures/tutorial_table_view_create.png
   :align: center

Save the definition of the view and now click in the *Table* button in the
operations for a vew. The appropriate table subset is shown. The buttons at the
top of the page allow you to edit the view (change the rows and columns
selected), or select another available view.

.. figure:: ../scaptures/tutorial_table_view.png
   :align: center

Column and Row Statistics
-------------------------

If you click in the button with the column name in any of the table view and
select the *Statistics*, OnTask shows a page with an statistical description
of the values in that column. The analogous option is available through the
*Operations* button in the row (left side of the table view). The page shows
identical representations than in the case of the column stats, but for each
column the words *Your value* appear in the location corresponding to the value
in the row.

.. figure:: ../scaptures/tutorial_row_statistics.png
   :align: center

Actions
=======

Access the *Actions* page clicking in the link with the same name in the  top
of the screen. The next screen shows the list of actions that are part of
the workflow, and the buttons to create a new one, import, or manage the data
table.

.. figure:: ../scaptures/tutorial_action_index.png
   :align: center

Personalized text action
------------------------

Click on the button to create a *New Action*, provide a name, a description
(optional) and select the type *Personalized text*.

.. figure:: ../scaptures/tutorial_personalized_text_create.png
   :align: center

The next screen is the *personalized text action editor*. The functions are
divided into three areas.

.. figure:: ../scaptures/tutorial_personalized_text_editor.png
   :align: center

1. This section allows to define a *filter*, or a condition to select a subset
   of the learners for which this action will be considered.

2. This section contains the conditions to be used in the personalized text.

3. This area is the HTML text editor to write the content to personalize.

Place the cursor in the text area and start the text with a salutation. Then
click in the pull down menu next to *Insert* with the value *Column name*.
Select the column *GivenName*. The string `{{ GivenName}}` appears
in the text area. This notation is to instruct the next steps to replace the
value among double curly braces with the name of each student.

.. figure:: ../scaptures/tutorial_personalized_text_editor_with_column.png
   :align: center

Click now in the button *New* in the condition area. A form appears to
introduce the name, description and formula. The formula may contain any
combination of Boolean operators with respect to the column values. For
example, the condition::

  Program equal to FASS

can be encoded in the formula widget as shown in the following figure

.. figure:: ../scaptures/tutorial_condition_program_FASS.png
   :align: center

We now use this condition to control the appearance of text in the editor.

- Write a sentence in the editor below the greeting.

- Select it

- Click in the arrow button next to the condition name and select *Insert in
  text*.

.. figure:: ../scaptures/tutorial_personalized_text_condition_inserted.png
   :align: center

The text area is then surrounded by two marks::

  {% if Program is FASS %}Here are some suggestions for FASS{% endif %}

This is the format to instruct the processing step to check the value of
the condition ``Program is FASS`` and include the surrounded text only if
the condition is true.

Repeat the procedure and create three more conditions such that they are true
if the value of the *Program* columns is equal to *FSCI*, *FEIT*, and *SMED*
respectively. Insert three more messages in the text area that are controled
by their respective conditions. At the end, each sentence will be surrounded
by text referring to each of the four conditions you created:

.. figure:: ../scaptures/tutorial_personalized_text_condition_inserted2.png
   :align: center

Selecting only a subset of learners
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In some cases, you may want to create a personalized text only for a subset of
the learners. This can be done defining a *Filter* at the top of the screen
(area 1). For example, the following filter:

.. figure:: ../scaptures/tutorial_personalized_text_filter.png
   :align: center

selects only those learners for which the column *Attendance* in the table
has the value *Full Time*. Upon closing the small window with the filter
data, the editor screen contains information about how many learners are
being selected by that filter.

.. figure:: ../scaptures/tutorial_personalized_text_editor2.png
   :align: center

The application will show a message if the filter excludes all the learners
(none of them satisfy the condition given in the filter).

The text in the editor will be processed for each row in the table (or the
subset specified by the filter) and all conditions and fields will be evaluated
with the values in that row. In other words, if a sentence is
surrounded by one condition, the condition is evaluated replacing the column
names by the values in the row. If the condition is *True*, the text will
appear, and if not, it will be ignored.

The botton with name *Preview* at the bottom of the editor allows you to see
the text resulting from the evaluation of each row.

.. figure:: ../scaptures/tutorial_personalized_text_preview.png
   :align: center

The bottom part of the screen shows the values of those columns that were
used to evaluate the conditions required in the text. You may use the arrows
at the top of the screen to review the message and see how it is changing
from learner to learner.

Sending Emails
^^^^^^^^^^^^^^

Once you have created a personalized text, you may want to send emails to the
learners (or the subset selected by the filter, if defined). First click in
the *Save* button to store the content of the the personalized text. The
platform shows the page with all the actions in the workflow. Click in the
button with name *Email* in the operations of the action you just created. The
following form appears in the screen:

.. figure:: ../scaptures/action_personalized_text_email.png
   :align: center

The form allows you to specify eight fields:

Email subject
  String to use as subject for all the emails.

Column to use as email address
  This is the name of the column in the table from where to extract the email
  address to use in the *To* field of the email.

Comma separated list of CC emails
  This is useful when you want to send the emails with copy to other users.
  The CC emails must be separated by commas (e.g. *user1@bogus.com,
  user2@bogus.com*)

Comma separated list of BCC emails
  Field analogous to the previous one except that the values are used in the
  blind copy of the email.

Send you a summary message?
  If selected platform will send you (the email you used to log in) a message
  with a summary of the operation once all emails are sent.

Track email reading in an extra column?
  If selected the platform will insert an extra column in the table
  containing the number of times each email has been opened (this counter,
  though, may not have a correct value as it depends on the configuration of
  external programs)

Download a snapshop of the worfklow
  When selected, the platform saves the workflow in its current state. This
  function is useful to keep an exact replica of the state of the actions,
  conditions and data when the data was sent. The resulting file can then be
  imported (see the *Import workflow* in the home page) to check the content
  of the emails.

Check/exclude email addresses before sending
  If selected the platform will offer you a last chance to specify some email
   addresses to *exclude* from the emails. This may be useful if you want to
   remove a small amount of addresses that you know they should not be
   considered but they cannot be easily removed with the use of the action
   filter.

The button *Preview* at the bottom of the page offers the same functionality
than in the editor, preview the final appearance of the messages that will be
sent out to the learners (with the subject).

Making content available through OnTask
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An alternative to send an email is to make the personalized text available
through a URL that is provided by OnTask. This URL can be enabled by clicking
in the *URL* button of the action operations.

.. figure:: ../scaptures/tutorial_personalzed_text_URL.png
   :align: center


If learners are allowed to connect to OnTask (they have an account), their
email is part of the data stored in the workflow,  and the access to the
platform can be done through a Single Sign-on system (e.g. LTI through a
learning management system), the URL shown in the  previous figure will allow
them to access the personalized text.

Surveys and/or Polls
--------------------

Personalized texts can be very powerful to offer students content, comments,
or point them to resources selected based on the available data. This data
may come from sources such as student information systems or the learning
management system. However, in some cases we would like to obtain data either
directly from the students, or perhaps from the instructors through
observation. This functionality is offered in OnTask through the actions
called *Surveys*. These surveys collect information from the students (or the
instructors) through conventional web forms and the data is automatically
added to the workflow table and available to be explored through the
dashboard or statistics.

The first step to create a survey is to go to the *Actions* page, click in
the *New action* button, provide a name, a description (optional) and select
the action type *Survey*:

.. figure:: ../scaptures/tutorial_survey_create.png
   :align: center

After the survey is created, the following screen is shown

.. figure:: ../scaptures/tutorial_survey_editor.png
   :align: center

The editor is divided into five areas:

Filter learners
  An expression identical to the one used in the personalized text to select a
  subset of the learners for which the will be available.

Description
  Text describing the survey that is shown to the learners.

Key column to identify learners
  The key column in the table that will be used to identify the users when
  submitting their answers. This is typically the column that contains the
  user email.

Shuffle questions
  If selected, the questions in the survey will be shuffled when shown to the
  learners.

Columns to obtain and store the data
  The columns used to collect the data. In this action, a column is
  equivalent to a question. The description of the column is the text of the
  question. In this part of the editor you may either use one of the
  existing columns as question, create a new column (or
  question), or create a new derived one (the initial values are created by
  combining values from other columns).

This page will show you a warning message if any of the columns used in the
survey has an empty description. Let's suppose you want to ask the learners
two questions:

- What was the most challenging topic for you this week? 

- What was your dedication to the course this week?

To make the data suitable for further processing, we will create the two
questions/columns with a set of pre-defined answers. Use the *Add new column*
button to create two columns of type string and provide the allowed answer
values as a comma-separated list.

.. figure:: ../scaptures/tutorial_survey_column_creation.png
   :align: center

After creating the column, insert it in the survey by selecting it with the
pull down menu. Repeat the procedure for the second question/column. You can
now add these columns to the action and the editor will show them in the
table at the bottom as shown in the following figure:

.. figure:: ../scaptures/tutorial_survey_editor2.png
   :align: center

As in the case of the personalized text action, the *Preview* button allows
you to verify how will the learners see the content:

.. figure:: ../scaptures/tutorial_survey_preview.png
   :align: center

Once created, you may select the URL from the action as it was described for
the personalized text and make it available for learners to enter their
answers. The data will be automatically added to the table.

The *Run* button in the survey actions allows an instructor to introduce the
survey answers for multiple learners. This functionality is used for
instructors to enter observations when interacting with learners. The table
search functionality allows to find the learners quickly and then click in
their survey execution and enter the data.

Combining personalized text and surveys
---------------------------------------

The information collected through surveys can be used in a personalized text
action. The survey data is stored in regular columns in the table. These
columns can then be used as part of the conditions or filter in a
personalized text. For example, the information collected as answers to the
question *What was the most challenging topic for you this week?* can be used
to select a set of adequate links to resources to help learners with the
given topic.

Scheduling Emails
=================

Work in progress.

Merging Data
============

Work in progress

Uploading Data from a Remote Database
=====================================

Work in progress

Plugins: Write your own data processing code
============================================


Example: A Predictive Model
---------------------------

Suppose that your favorite data analyst has processed the data set and created a predictive model that estimates the score of the final exam based on the value of the column *Contributions* applying the following linear equation::

  final exam score = 3.73 * Contributions + 25.4

You would like to incorporate this model to the workflow and use the predicted final exam score as another column to create conditions and personalize content. One way to achieve this is by creating a plugin that given the two coefficients of a linear model (in the example 3.73 and 25.4) returns a new data set with a column with the values obtained using the corresponding equation. In order for the plugin to comply with the  :ref:`requirements <plugin_requirements>`, one possible definition would be:

.. literalinclude:: ../../src/plugins/test_plugin_1/__init__.py
   :language: python

Application Programming Interface (API)
=======================================

Work in progress

