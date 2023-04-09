.. _workflow_settings:

Additional Workflow Operations
******************************

In addition to the operations described in the previous sections to upload and merge data, create actions, and run these actions, there are additional operations for the workflow that can be accessed through the *More* pull-down menu in the top-bar menu. The settings pages offer information about: workflow operations (export, rename, clone, etc.), column operations (change column type, rename, clone, etc.), scheduled actions, and view logs.

.. include:: include_details.rst

.. _scheduler:

Scheduled Actions
=================

   "I have no regular schedule. I get up whenever I can."
   -- Jimmy Wales


The :ref:`personalized text <personalized_content>`, :ref:`personalized canvas email <personalized_canvas_email>`, :ref:`send list through email <email_report_action>`, :ref:`personalized JSON object <personalized_json>` and :ref:`send JSON report <json_report_action>` actions can be scheduled to run at some point in the future. To schedule the execution of an action go to the |bi-chat-right-quote-fill| *Actions* page from the top menu, click on the icon with three dots in the right-most column of the action and select the operation |bi-calendar| *Schedule*.

When scheduling the execution of an operation, the following fields are always requested at the top of the form:

Name
  A name to identify this scheduling (a user may have several of these actions pending in a workflow)

Description
  A brief description explaining this scheduled action (for example, "send reminder before the exam")

When to execute the action
  A date/time in the future when the action will be executed.

Multiple executions?
  Check this box if you want the action to execute more than once. You may define the a start and stop date, and a expression with the frequency of execution.

.. _schedule_email:

Scheduling a Personalized Text Action
-------------------------------------

The following figure shows the information requested to schedule the execution of a personalized text action (sending emails to learners):

.. figure:: /scaptures/schedule_action_email.png
   :align: center

The additional fields in this form are:

Column containing email
  The column in the table used to fill out the destination email. OnTask will check that the values in that column are proper email addresses.

Email subject
  The text to be included in the email subjects.

Comma separated list of CC emails
  A comma separated list of emails to include in the *carbon copy* (or CC) field of the email.

Comma separated list of BCC emails
  A comma separated list of emails to include in the *blind carbon copy* (or BCC) field of the email.

Send confirmation email
  Select this option if you want a confirmation email sent to you.

Track when emails are read
  Try to detect if the email is read. OnTask adds an extra column to the table to store the number of times the message is opened. This detection relies on how the email client processes the message, therefore, the information in this column may not be accurate.

Check/exclude emails
  If selected, this option inserts an extra step showing the emails and offering the possibility to eliminate them from the action. This option is useful to perform a final check and remove emails that cannot be removed with the action filter.

.. _schedule_json:

Scheduling a Personalized JSON Action
-------------------------------------

The following figure shows the information requested to schedule the execution of a personalized JSON action (sending JSON object to another platform):

.. figure:: /scaptures/schedule_action_json.png
   :align: center

The additional fields in this form are:

Column to select elements
  A column to show its values and allow to review and exclude some of the entries. This option is useful to perform a final check and remove entries that cannot be removed with the action filter.

Authentication Token
  The string to be use to authenticate with the external platform.

.. _schedule_canvas:


Scheduling a Personalized Canvas Email Action
---------------------------------------------

If OnTask is :ref:`appropriately configured <canvas_email_config>` to send emails using the Canvas API, the actions can be scheduled providing the information through a form as shown in the following figure.

.. figure:: /scaptures/scheduler_action_canvas_email.png
 :align: center

The fields in this form are:

Name
A name to identify this scheduling (not to be confused with the name of the action that has already been selected).

Description
A brief description explaining this scheduled action (for example, "send reminder the night before the exam).

Column in the table containing the Canvas ID
This field is mandatory because OnTask needs to know which column to use to differentiate the emails to send to Canvas.

Email subject
Text to include as subject of the message.

When to execute the action
A date/time value in the future.

.. _scheduler_menu:

Table with Scheduled Actions
----------------------------

The table showing all the action scheduling operations can be access through the *More* link in the top-bar menu selecting the |bi-calendar| *Scheduled operations* link. The list of scheduled actions is shown as illustrated in the following figure.

.. figure:: /scaptures/schedule.png
   :align: center
   :width: 100%

The operations available for each scheduled execution are:

|bi-pencil-fill| Edit
  Edit the elements in the scheduled operation.

|bi-eye-fill| View details
  View all the details for this scheduled execution (includes values in the payload)

|bi-trash-fill| Delete
  Delete the scheduled execution.

.. _logs:

View logs
=========

The platform keeps a log of most of the operations that are executed when managing a workflow. These records are available through the *View Logs* link in the *More* pull down menu at the top-bar menu. The page shows information about the records in tabular form. The following figure shows an example.

.. figure:: /scaptures/logs.png
   :align: center
   :width: 100%

The |bi-download| *CSV Download* button allows to download the logs in CSV format for further processing. Additionally, the content of the table is paginated and the links to access each page are shown at the button. The records can be searched using the box at the top right corner of the table.
