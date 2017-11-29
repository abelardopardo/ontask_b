.. _tutorial:

===============
OnTask Tutorial
===============

Before you start the tutorial make sure you have an account in an OnTask instance and you have instructor privileges (create workflows, actions, etc). Also, download the file :download:`learner_information.csv <../Dataset/learner_information.csv>` that contains a synthetic data set with information about learners, participation in a discussion forum, engagement with activities, and some additional features.

Remember the three central concepts in OnTask:

Workflow
  A container with the data (matrix), a set of procedures to manipulate columns, data upload and a set of actions. This container is typically associated with a course, but it could also model an entire institutional degree.

Matrix
  A two-dimensional structure in which each row represents a learner, and each column a learner attribute such as the score in an assessment, class attendance, number of interventions in the discussion forum, engagement with videos, etc.

Actions
  An action is a HTML resource of which certain parts that are included or excluded based on a set of **conditions** created with the learner attributes (for example, number of interventions in the forum is larger than five, and number of times a video was watched is larger than 2).

The following figure represents the high level view of the tool.

.. figure:: drawing.png
   :align: center

The process to create a personalised text is divided into four stages:

Upload the data
  We will use a :download:`CSV file with the learners data <../Dataset/learner_information.csv>`about several activities in a course. In this first stage you will upload the data into a matrix and identify certain special columns (those that provide a unique reference to a learner such as the learner ID)

Review the data matrix
  In this stage you will explore the values in the matrix.

Create an action
  In this stage you will create an action with various conditions that will be applied to the text of a personalised email message.

Review the messages
  And finally you will review the appearance of these messages for different
  learners.

The following steps describe the required operations in each of these stages.

Create a new workflow
---------------------
Log into the tool and click in the tool icon on the top left corner of the screen. If you have an instructor account, you will see the button to create a new workflow as shown in the following figure.

.. figure:: ../Ontask_screens/01_home_create_workflow.png
:align: center

The icon in the top right corner next to your profile image is a link to the OnTask documentation. Click in the button to create a new workflow and enter its name and a description.

.. figure:: ../Ontask_screens/02_new_workflow_name.png
   :align: center

Once you created the workflow the platform shows the list of all the
workflows available.

.. figure:: ../Ontask_screens/02_b_workflow_table.png
   :align: center

The first step is to select or *open* a workflow by clicking on the name to
manipulate it. Once this operation is done, the access to the element is
blocked for any other users (in case the workflow is being shared) to
prevent two users changing the data or the actions simultaneously. The following screens will show the name of the selected workflow at the top. If you want to select another workflow to manipulate, you simply click in the OnTask icon at the top left corner of the screen to go back to the initial table.

Open a workflow
---------------

When you open a workflow, a page with its details is shown like the one in
the following figure

.. figure:: ../Ontask_screens/03_data_initial.png
   :align: center

You can see the icon on the top right corner that links to the initial
page, and the icon in the top left corner that links to the documentation.
So far the page only shows the description of the workflow and the last
time it was modified because no data has been uploaded.

The top of the screen now shows the sections offering different operations
over the workflow:

Details
  Is the current page with information about the columns, data types,
  number of actions, etc.

Matrix
  Operations to visualise and manipulate the matrix (search for values,
  add a row, add a column)

Actions
  Operations to create the actions and conditions.

Logs
  A table showing the history of operations performed on this workflow

The buttons immediately under title *Workflow Details* show some of the
operations available at this point:

- :ref:`New column <details_add_column>`

- :ref:`Attributes <details_attributes>`

- :ref:`Share <details_sharing>`

- :ref:`Export <details_export>`

- :ref:`Rename <details_rename>`

- :ref:`Delete <details_rename>`

Data Upload
-----------

We now upload the data included in the file :download:`learner_information.csv <../Dataset/learner_information.csv>`. Click in the *Dataops* menu, and then in the option to *CSV Update/Merge* as shown in the following figure

.. figure:: ../Ontask_screens/05_data_csvupload_initial.png
   :align: center

The next screen asks you to choose a file to upload the data.

.. figure:: ../Ontask_screens/05_b_data_csvupload_initial.png
   :align: center

Choose the file :download:`learner_information.csv <../Dataset/learner_information.csv>` and proceed to the next step. The next screen shows a table with the
name of the detected columns, the type (also automatically detected), a
pre-filled field with the column name (in case you want to change it), and if
 it is a *key column* (there are no repeated values in all the rows).

   .. figure:: ../Ontask_screens/06_data_csvupload_student_list.png
      :align: center

The *key* columns are highlighted because a workflow must have at least one column of this type in its matrix. Select all the column (clicking in the top element labeled *load*) and click on the *Finish* button, and then back to the
*Details* page to see the summary of the information in the workflow.

You can now see the information about the columns present in the workflow as
shown in the follogin figure

.. figure:: ../Ontask_screens/07_data_view_student_external.png
   :align: center

For each column you can change its name, description, type and key
attributes, or delete it from the workflow (icons in the left most column of
the table).

Browsing the matrix
-------------------

Once the data has been uploaded, click in the *Matrix* link at the top of the screen. The following screen shows the values stored in the matrix

   .. figure:: ../Ontask_screens/18_matrix_initial.png
      :align: center

FIX FIX FIX

#. The area at the bottom of the screen allows to filter values in the columns to do some basic data exploration as shown in the following figure.

   .. figure:: ../Ontask_screens/19_matrix_search_column.png
      :align: center

#. The matrix can also contain *custom attributes* that are simply pairs of (name, value) that can be needed when writing the emails. Click in the item *Custom Attributes* at the top of the screen and then *Add Attribute* as shown in the following figure:

   .. figure:: ../Ontask_screens/20_matrix_custom_attributes_initial.png
      :align: center

#. Enter the name *Course Coordinator* and a value in the text boxes. Finish the insertion by clicking in the *Submit* button.

   .. figure:: ../Ontask_screens/21_matrix_custom_attribute_add.png
      :align: center

#. We are now ready to proceed to the third stage (creating the rules) by clicking in the **Rules** item in the menu on the left side of the screen.

   .. figure:: ../Ontask_screens/22_rule_initial.png
      :align: center
      :width: 40%

   The new rule needs a name and a description to help you manage several of them within the workflow.

   .. figure:: ../Ontask_screens/23_rule_create.png
      :align: center
      :width: 40%

   Once the rule has been created, edit its content by clicking in the *Edit* item.

   .. figure:: ../Ontask_screens/24_rule_operations.png
      :align: center
      :width: 40%

#. The following screen is one of the most complex in the tool. It allows you to write an email with special fields in it, and a set of conditions to control those fields. The first step is simply to write the opening of an email, and then insert the name of the student. You can do this by (1) placing the cursor in the appropriate location in the message, (2) selecting the column value you want to insert, in this case *GivenName*, and (3) clicking in the button *Insert Data Field* as shown in the following figure.

   .. figure:: ../Ontask_screens/25_rule_insert_data_field.png
      :align: center

   These steps insert the string ``{{GivenName}}`` in the email window which is simply a *place holder* that will be replaced by the actual value of that field for the student when the email is sent.

#. The next step is to create a condition. Click in the button *Add Condition* and a widget will appear to create a boolean condition. The condition first needs a name at the top (to be able to refer to it within the message) and then an expression that is either True or False. In the following figure the condition is::

     Q01 is equal to 0 AND Q02 is equal to 0

   Click in the button *+ ADD RULE* to add the clauses and select the appropriate field name and values. Once the expression is created, click in the *Verify Condition* button and see how it appears in the pull down menu on the right side of the screen as shown in the following figure.

   .. figure:: ../Ontask_screens/26_rule_condition_edit.png
      :align: center

#. Once the condition has been inserted (and verified), we can use it in the email area. Write a sentence in the email notifying the student that it follows some comments about their midterm exam. Once the cursor is placed after that sentence, select the condition you just introduced in the right side of the screen in the pull down menu and then click in the button *Insert Condition*. You will see the following *place holder* string appear in the screen::

     {{Failed topic 1: True} : : { Insert condition text here }}

   The text ``Insert condition text here`` is for you to replace with the appropriate text that will appear in the message if the given condition is equal to True (or False if you select it in the menu above). The following figure shows the result of these operations.

   .. figure:: ../Ontask_screens/27_rule_insert_condition_inemail.png
      :align: center

#. In a way similar to the name of the student, you may insert any of the *Custom Attributes* you defined for the matrix. For example, you may write the end salutation of the message and then select the course coordinator in the upper menu next to the button *Insert Custom Attribute* and click to insert it in the text as shown in the following figure.

   .. figure:: ../Ontask_screens/28_rule_insert_attribute.png
      :align: center


   As in the previous cases, the string ``{{Custon-Course Coordinator}}`` is a place holder that will be replaced by the name of the course coordinator.

#. Now try to add a more complex expression detecting of the student failed either Q01 or Q02 (that is, if either of them is equal to zero, but not both!). Do not forget to provide a name for the condition and to click in the ``Verify Condition`` button when done. Once you created the condition, and repeating the steps previously described, insert another text in the email that appears only if this new condition is True. The result of these steps should be something similar to what is shown in the following figure:

   .. figure:: ../Ontask_screens/29_rule_insert_complex_condition.png
      :align: center


   You can add a third rule to capture the case in which both Q01 and Q02 are equal to 1. This way you cover all possibilities and all students receive the message with personalised text.

#. Once you have the message with the finished text and the right conditions, you can save the rule as shown in the following figure.

   .. figure:: ../Ontask_screens/31_rule_save.png
      :align: center

#. The next step is to test the rule and see if the message is correctly built for each student. You may click in the ``Test`` button at the top of the rule screen as shown in the following figure.

   .. figure:: ../Ontask_screens/32_rule_test.png
      :align: center

#. To see the effect of this test, you need to go back to the rules page (click in the menu item **Rues** in the left side of the screen), and then click to see the summary as shown in the following figure.

   .. figure:: ../Ontask_screens/33_rule_summary.png
      :align: center
      :width: 40%

#. Once you see the list of students and messages, you can click in the button with name ``Show`` to see the actual text that was created for that student.

   .. figure:: ../Ontask_screens/34_rule_summary_show.png
      :align: center

#. Create a new rule in which the email is not sensitive to the results of the questions in the midterm, but to the activity in the forum.

#. Share your new message with your peers.
