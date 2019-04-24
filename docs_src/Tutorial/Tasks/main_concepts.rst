.. _central_concepts:

Main elements in OnTask
***********************

OnTask contains three central concepts:

Workflow
  A workflow is simply an entity that contains a data table and a set of actions. The most intuitive interpretation is to assign a workflow to a *course*. An instructor may participate in various courses. Each of them has a different set of students. A workflow will contain the data about the students in a course, and the actions that are appropriate for that course. After opening a session in OnTask, the user manages a collection of workflows. At this level the platform allows for the creation, modification, deletion, sharing and cloning of workflows. Most of the operations require the user to first *open* the workflow.

Table
  Each workflow has a data table, a two-dimensional structure in which each row represents a learner, and each column a learner attribute such as the score in an assessment, class attendance, number of interventions in the discussion forum, engagement with videos, etc. The operations over the table allow to create, rename, delete, change the data type, or clone a column, the creation of a table view showing a subset of the data, etc. A table in the workflow must have **at least** one :ref:`key column<key_columns>`. Key columns are marked as such in the workflow. This mark can be removed as long as it is not the only remaining key column in the table. Any column can be turned into a key column as long as all its values are non-empty and unique for each row.

Actions
  An action in OnTask can be:

  * A HTML text in which certain parts that are included or excluded based on a set of **conditions** created with the learner attributes (for example, number of interventions in the forum is larger than five, number of times a video was watched is larger than 2, etc). The purpose of this text is to make it available to the learners.

  * A set of questions or a survey that is offered to the learners to answer. Upon receiving the responses, the information is incorporated to the workflow table. The survey can also be used by the instructor to capture observations.

  * A `JSON object <https://json.org>`_ representing a set of information fields. The values of these fields can be included, excluded or changed depending on a set of **conditions** created with the learner attributes (analogous to those described for the HTML text). This object can be sent it to an external platform for further processing.

The following figure illustrates the high level view of OnTask.

.. figure:: /scaptures/high_level_view.png
   :align: center


