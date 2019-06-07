.. _plugin_write:

Write your own data processing code
***********************************

Example: A Predictive Model
===========================

Suppose that your favorite data analyst has processed the data set and created a predictive model that estimates the score of the final exam based on the value of the column *Contributions* applying the following linear equation::

  final exam score = 3.73 * Contributions + 25.4

You would like to incorporate this model to the workflow and use the predicted final exam score as another column to create conditions and personalize content. One way to achieve this is by creating a plugin that given the two coefficients of a linear model (in the example 3.73 and 25.4) returns a new data set with a column with the values obtained using the corresponding equation. In order for the plugin to comply with the  :ref:`requirements <plugin_requirements>`, one possible definition would be:

.. literalinclude:: /../src/plugins/linear_model/__init__.py
   :language: python

The steps to *run the model* are:

- Click in the |fa-table| *Table* icon in the top menu and select the option *Run model*. The table will include those models ready for execution.

.. figure:: /scaptures/dataops_model_list.png
   :align: center

- Click in the name of the model. The next screen contains four tabs:

  Input columns to transformation
    Select the columns to use as input data for the model.

  Columns to store the result
    Provide a set of columns to store the result of running the model and one key column to merge the results with the existing table (**mandatory**).

  Parameters
    A set of parameters to execute the model (could be empty).

  Description
    A more detailed description of what the model does.

- Select the appropriate elements and click in the |fa-rocket| *Run* button above the form.

- The model is executed in the background (it may take some time to execute) and the result is merged into the workflow table.



