.. _actions:

Actions
=======

Access the *Actions* page clicking in the link with the same name in the top
of the screen. The next screen shows the list of actions that are part of
the workflow, and the buttons to create a new one, import, or manage the data
table.

.. figure:: ../../scaptures/tutorial_action_index.png
   :align: center

Personalized text action
------------------------

Click on the button to create a *New Action*, provide a name, a description
(optional) and select the type *Personalized text*.

.. figure:: ../../scaptures/tutorial_personalized_text_create.png
   :align: center

The next screen is the *personalized text action editor*. The functions are
divided into three areas.

.. figure:: ../../scaptures/tutorial_personalized_text_editor.png
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

.. figure:: ../../scaptures/tutorial_personalized_text_editor_with_column.png
   :align: center

Click now in the button *New* in the condition area. A form appears to
introduce the name, description and formula. The formula may contain any
combination of Boolean operators with respect to the column values. For
example, the condition::

  Program equal to FASS

can be encoded in the formula widget as shown in the following figure

.. figure:: ../../scaptures/tutorial_condition_program_FASS.png
   :align: center

We now use this condition to control the appearance of text in the editor.

- Write a sentence in the editor below the greeting.

- Select it

- Click in the arrow button next to the condition name and select *Insert in
  text*.

.. figure:: ../../scaptures/tutorial_personalized_text_condition_inserted.png
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

.. figure:: ../../scaptures/tutorial_personalized_text_condition_inserted2.png
   :align: center

Selecting only a subset of learners
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In some cases, you may want to create a personalized text only for a subset of
the learners. This can be done defining a *Filter* at the top of the screen
(area 1). For example, the following filter:

.. figure:: ../../scaptures/tutorial_personalized_text_filter.png
   :align: center

selects only those learners for which the column *Attendance* in the table
has the value *Full Time*. Upon closing the small window with the filter
data, the editor screen contains information about how many learners are
being selected by that filter.

.. figure:: ../../scaptures/tutorial_personalized_text_editor2.png
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

.. figure:: ../../scaptures/tutorial_personalized_text_preview.png
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

.. figure:: ../../scaptures/action_personalized_text_email.png
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

.. figure:: ../../scaptures/tutorial_personalzed_text_URL.png
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

.. figure:: ../../scaptures/tutorial_survey_create.png
   :align: center

After the survey is created, the following screen is shown

.. figure:: ../../scaptures/tutorial_survey_editor.png
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

.. figure:: ../../scaptures/tutorial_survey_column_creation.png
   :align: center

After creating the column, insert it in the survey by selecting it with the
pull down menu. Repeat the procedure for the second question/column. You can
now add these columns to the action and the editor will show them in the
table at the bottom as shown in the following figure:

.. figure:: ../../scaptures/tutorial_survey_editor2.png
   :align: center

As in the case of the personalized text action, the *Preview* button allows
you to verify how will the learners see the content:

.. figure:: ../../scaptures/tutorial_survey_preview.png
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


