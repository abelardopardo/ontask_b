.. _using:

**************
Using the tool
**************

In a nutshell, the idea of OnTask is to help instructors, learners and designers to exchange data  about what is happening in a learning experience to design and deploy personalized learner support actions. This last term, *personalized support actions* is purposefully vague to include any action that is offered to learners in different forms depending on personalized conditions. The typical *workflow* to use OnTask starts by uploading and combining available data about the learning experience, either provided through some platform (LMS, video platform), provided by the students (questionnaires), or reported by the instructors. The instructors then write simple rules to select a subset of students and create a resource (HTML page, a message, a visualization) so that its content depends on the data available for each learner. The following figure shows an illustration of this workflow:

.. figure:: ontask_workflow.png
   :align: center
   :width: 100%

Imagine a learning experience in which you want to provide personalized messages to the learners in three instances. In the first week, you want to send a welcome email and change slightly the text based on the student background (courses taken before this one). The second week you want to send some comments and suggestions about the participation in the forum and the text will depend on the measures of engagement obtained from the platform. Finally, you want to send a third personalized email depending on the level of engagement with the videos in the course. The idea of these messages is that you want to change the text in the message for each learner based on the information stored in the table.

The main entity in the platform is a :ref:`*workflow* <workflow>` and represents a set of data capturing procedures, a table with current data, and a set of actions. The usual steps require first to populate the table with data extracted from the learning environment. In the figure we assume a variety of data sources ranging from those coming from the use of technology, self-reported by the students, or observed and reported by the instructors.

These three sources are combined and stored in the second entity in OnTask: the table. Think of the table as a conventional excel sheet storing the information about the learners (one learner per row and a set of features about each learner as columns).

The third entity in OnTask is the *personalized action* that is a text with elements that are selected and adapted to each learner based on a set of basic rules that depend on the student features stored in the table. This text can be included in an email, made available through a web page, or forwarded to another system for further processing.

A workflow in OnTask contains a single table (rows and columns) and a set of actions. This container is conceived to manage the data and actions related to a learning experience. You may use the workflow shown in the documentation importing  the :download:`ELON3509 workflow <../../initial_workflow.gz>`.

The following sections offer a more in-depth description of all these elements as well as examples with real scenarios.

.. toctree::
   :maxdepth: 2
   :caption: More detail information about the following elements:

   workflow
   details
   dataops
   table
   actions
   scheduler
   logs
