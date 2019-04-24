.. _tut_scheduling:

Scheduling Actions
******************

Log in the platform, open a workflow with data and actions, and click in the *Actions* link on the top menu. Sometimes the execution of the actions that produce personalized content (either text or a JSON object) need to be scheduled for some specific point in time and proceed without any instructor intervention. Choose one of these actions and in the *Actions* page click in the link *More* in the operations column. The first operation that appears is *Schedule*. Click on that link.


Scheduling Personalized Text Actions
====================================

If the action is a personalized text, the screen requests information to execute the action but including a field stating when to execute it.

.. figure:: /scaptures/schedule_action_email.png
   :align: center
   :width: 100%

In the case of an action that produces personalized text, the :ref:`scheduling<schedule_email>` needs a name, description (optional), the column that contains the email addresses, the date/time of the execution (in the future), the email subject, comma separated list of CC and BCC email addresses, the choice if a confirmation email is sent, the option to track the emails, and the possibility of checking the list of emails to see if any of themm should be excluded. After introducing this information the request to execute the action is submitted to the system.

Scheduling Personalized JSON Actions
====================================

If the action is a personalized JSON, the screen requests information to execute the action but including a field stating when to execute it.

.. figure:: /scaptures/schedule_action_json.png
   :align: center
   :width: 100%

In the case of an action that produces a personalized JSON, the :ref:`scheduling<schedule_json>` needs a name, description (optional), a column used to select/deselect the elements, and an authentication token to send to the destination platform.

Checking the scheduled execution
================================

All the operations schedule for execution can be verified, edit and deleted from the link *Scheduler* through the top menu.

.. figure:: /scaptures/schedule.png
   :align: center
