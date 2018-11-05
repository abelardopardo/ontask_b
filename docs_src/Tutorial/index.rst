.. _tutorial:

Tutorial
********

The OnTask tutorial is organized as a set of tasks that are done using a set of files that contain data, actions, and other additional elements. Before attempting any of the tasks make sure you have an instructor account in an OnTask server and download and unpack the zip file :download:`dataset.zip <../Dataset/dataset.zip>`. Once unpacked, you should have a folder with the following files in it: ``student_list.csv``, ``midterm_results.csv``, ``forum_participation.csv``, ``blended_participation.csv`` and ``all_data.csv``. These files assume a hypothetical scenario shown in the following figure.

.. figure:: the_dataset.png
   :width: 100%
   :align: center

We assume that a learning experience is through its sixth week. From weeks 2 to 5 learners were engaging with two videos and to set of questions per week. In Week 6 students took a midterm examination consisting of 10 questions (about 5 topics, 2 question per topic). Additionally, during these six weeks a discussion forum has been available for them to make comments. The information contained in each file is:

``student_list.csv``
  File with student id (SID), Identifier (an auxiliary field), email, surname, given name, middle initial, gender, course code, program (`FSCI`, `FEIT`, `FASS` or `SMED`), type of enrolment (`HECS`, `Local` or `International`) and attendance (Full Time or Part Time).

``midterm_results.csv``
  File with student id (SID), email, last name, first name, the result of the 10 multiple choice questions (1 means correct, 0 means incorrect) and the total exam score (0-100).

``forum_participation.csv``
  File with student id (SID), days online, views, contributions and questions for weeks 2-5, and the accumulated value for all weeks.

``blended_participation.csv``
  File with student id (SID), Video, questions answered, and questions answered correctly (for two items) for weeks 2-5.

``all_data.csv``
  All data from the previous files properly combined into a single file.

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

.. figure:: drawing.png
   :align: center

The following tasks illustrate the different functionality available in OnTask for the scenario.

.. toctree::
   :maxdepth: 2
   :caption: Tasks:

   Tasks/create_workflow
   Tasks/open_workflow
   Tasks/data_upload
   Tasks/workflow_details
   Tasks/table
   Tasks/actions
   Tasks/scheduling
   Tasks/merging
   Tasks/database_upload
   Tasks/plugin_write
   Tasks/api
