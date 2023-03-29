.. _using:

Using OnTask
############

The idea behind OnTask is to help instructors, learners and designers to exchange data  about what is happening in a learning experience to design and deploy personalized learner support actions. This last term, *personalized support actions* refers to any action that is offered to learners in different forms depending on personalized conditions. The typical *workflow* to use OnTask starts by uploading and combining available data about the learning experience, either extracted from some platform (LMS, video annotation, quizzes), provided by the learners (questionnaires), or captured by the instructors. The instructors then write simple rules to select a subset of students and create a resource (HTML page, a message, a visualization) so that its content depends on the data available for each learner. The following figure illustrates of this workflow:

.. figure:: ontask_workflow.png
   :align: center
   :width: 100%

Imagine a learning experience in which you want to provide three personalized messages to the learners. In the first week, you want to send a welcome email and personalize slightly the text of this message based on the student background (courses taken before this one). The second week you want to send some comments and suggestions about the participation in the forum and the text will depend on the measures of engagement obtained from the platform. The third personalized email will vary depending on the level of engagement with the videos in the course. The idea of these messages is that you want to change the text in the message for each learner based on the information stored in the table.

OnTasks allows instructors to manage a set of **workflows**. A :ref:`workflow <workflow>` contains a **table** with data about the learners and a set of **actions**. After creating and opening a workflow you need to populate the table with data extracted from the learning environment. We assume that there several data sources (coming from the use of technology, self-reported by the students, or observed and reported by the instructors). These data sources are combined and stored in the **table**. Think of the table as a conventional excel sheet storing the information about the learners (one learner per row and a set of features about each learner as columns).

The other relevant entity in OnTask is the **action** that is either a set of questions to collect information from the learner or a text with elements that are selected or ignored based on **conditions** that are evaluated with respect to the learner student features stored in the table. This text can be included in an email, made available through a web page, or forwarded to another system for further processing.

The rest of the material in this section will use an :download:`initial workflow <../../initial_workflow.gz>` that can be downloaded and imported to your collection of workflows in OnTask.

.. toctree::
   :maxdepth: 2

   workflow
   data
   table
   action
   run
   workflow_ops
   plugins
