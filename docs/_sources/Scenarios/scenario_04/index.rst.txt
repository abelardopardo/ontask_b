.. _scenario_04:

Scenario 4: I want to change all actions at the same time
=========================================================

- CSV data file: :download:`Scenario 4 Data File <scenario_04_data.csv>`.

- Workflow data file: :download:`Scenario 4 Workflow File <scenario_04_wflow.gz>`.

Suppose you have a course with 500 students and they take the course as part of four programs named FASS, FEIT, FSCI, SMED in different disciplines. They are all related, but at the same time different. You would like to send them a text explaining the connection between the material studied in the course and their discipline. The have created four *Actions Out* each of them explaining the connection respectively with FASS, FEIT, FSCI and SMED. All of the actions are signed by *Sarah Johnson* as the course coordinator.

Now it turns out, Sarah is no longer the course coordinator and you have to change the signature of all four actions. But if you think of it, the way the actions are written produce **four points of change** instead of one. Can OnTask help you simplify this type of changes? Yes.



.. admonition:: Steps

   1. Import the workflow using the :download:`workflow file <scenario_04_wflow.gz>`.

   #. Select the workflow you just imported. You should be seeing the *Workflow Details* page.

   #. In the *More options* button at the top, pull down the options and select *Attributes*. A new page appears showing the collection of attributes available in the workflow. An attribute is nothing more than a pair with a name and a value.
