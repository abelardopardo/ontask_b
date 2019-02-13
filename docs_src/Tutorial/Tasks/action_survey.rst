.. _tut_surveys:

Surveys and/or Polls
********************

Personalized texts can be very powerful to offer students content, comments, or point them to resources selected based on the available data. This data
may come from sources such as student information systems or the learning management system. However, in some cases we would like to obtain data either
directly from the students, or perhaps from the instructors through observation. This functionality is offered in OnTask through the actions
called *Surveys*. These surveys collect information from the students (or the instructors) through conventional web forms and the data is automatically
added to the workflow table and available to be explored through the dashboard or statistics.

The first step to create a survey is to go to the *Actions* page, click in the *New action* button, provide a name, a description (optional) and select the action type *Survey*:

.. figure:: /scaptures/tutorial_survey_create.png
   :align: center
   :width: 60%

After the survey is created, the following screen is shown

.. figure:: /scaptures/tutorial_survey_editor.png
   :align: center

The editor contains three tabs:

Survey Questions
  The columns used to collect the data. In this action, a column is equivalent to a question. The description of the column is the text of the
  question. In this part of the editor you may either use one of the existing columns as question, create a new column (or
  question), or create a new derived one (the initial values are created by combining values from other columns).

Filter learners
  An expression identical to the one used in the personalized text to select a subset of the learners for which the will be available.

Survey Parameters
  This tab contains additional parameters for the survey, more precisely:

  Description
    Text describing the survey that is shown to the learners.

  Key column to identify learners
    The key column in the table that will be used to identify the users when submitting their answers. This is typically the column that contains the user email.

  Shuffle questions
    If selected, the questions in the survey will be shuffled when shown to the learners.

This page will show you a warning message if any of the columns used in the survey has an empty description. Let's suppose you want to ask the learners two questions:

- What was the most challenging topic for you this week? 

- What was your dedication to the course this week?

To make the data suitable for further processing, we will create the two questions/columns with a set of pre-defined answers. Use the |fa-plus| *Create question* button to create two columns of type string and provide the allowed answer values as a comma-separated list.

.. figure:: /scaptures/tutorial_survey_column_creation.png
   :align: center
   :width: 60%

Repeat the procedure for the second question/column. The result should be as shown in the following figure.

.. figure:: /scaptures/tutorial_survey_editor2.png
   :align: center

As in the case of the personalized text action, the *Preview* button allows you to verify how will the learners see the content:

.. figure:: /scaptures/tutorial_survey_preview.png
   :align: center
   :width: 60%

Once created, you may select the URL from the action as it was described for the personalized text and make it available for learners to enter their answers. The data will be automatically added to the table.

The *Run* button in the survey actions allows an instructor to introduce the survey answers for multiple learners. This functionality is used for instructors to enter observations when interacting with learners. The table search functionality allows to find the learners quickly and then click in their survey execution and enter the data.

