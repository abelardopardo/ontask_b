.. _central_concepts:

Main elements in OnTask
=======================

The three central concepts in OnTask are:

Workflow
  A container with the data (table), a set of procedures to manipulate columns, data upload and a set of actions. This entity is typically associated with a course, but it could also model an entire degree.

Table
  A two-dimensional structure in which each row represents a learner, and each column a learner attribute such as the score in an assessment, class attendance, number of interventions in the discussion forum, engagement with videos, etc.

Actions
  An action in OnTask can be one of two entities:

  * A HTML resource of which certain parts are included or excluded based on a set of **conditions** created with the learner attributes (for example, number of interventions in the forum is larger than five, and number of times a video was watched is larger than 2).

  * A set of questions that are shown to the students and their answers are incorporated to the data table.

The following figure represents the high level view of the tool.

.. figure:: /scaptures/high_level_view.png
   :align: center


