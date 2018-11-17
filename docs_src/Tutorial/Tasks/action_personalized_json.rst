.. _tut_personalized_json_action:

Personalized JSON action
========================

The second type of action available in OnTask is called *personalized JSON*. Create a new action and select this type from the pull-down menu when introducing the name and description.

.. figure:: /scaptures/tutorial_personalized_json_create.png
   :align: center

The following screen contains the editor for these actions.

.. figure:: /scaptures/tutorial_personalized_json_editor.png
   :align: center

The content is divided into three areas (similar to the ones used to edit :ref:`personalized text actions<tut_personalized_text_action>`.

1. This section allows to define a *filter*, or a condition to select a subset of the learners for which this action will be considered.

2. This section contains the conditions to be used to conform the personalized JSON object. Two conditions have been defined in the example. The first one with name ``Less than 50 in the midterm`` is exactly stating that condition, those students for which the score in the midterm has been less than 50. The second condition is the complementary, those students for which the midterm score has been greater or equal than 50. These conditions are used in the definition of the object in the screen area below.

3. This area is JSON object editor. In the previous figure you see an example of an object that contains three string/value pairs. The first two values are extracted from columns ``SID`` and ``Total`` respectively. The last field with name ``msg`` is defined using the conditions created in the second areaw of this screen.

The *Target URL* field captures the URL to use to send these JSON objects. The action will not be executed unless there is a non-empty value in this field.

As in the case of the :ref:`personalized text actions<tut_personalized_text_action>`, the *Preview* button at the bottom of the screen allows you to preview the resulting JSON objects for the selected rows of the data table.

.. figure:: /scaptures/tutorial_personalized_json_preview.png
   :align: center

