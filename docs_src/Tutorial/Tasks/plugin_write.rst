.. _plugin_write:

Plugins: Write your own data processing code
============================================


Example: A Predictive Model
---------------------------

Suppose that your favorite data analyst has processed the data set and created a predictive model that estimates the score of the final exam based on the value of the column *Contributions* applying the following linear equation::

  final exam score = 3.73 * Contributions + 25.4

You would like to incorporate this model to the workflow and use the predicted final exam score as another column to create conditions and personalize content. One way to achieve this is by creating a plugin that given the two coefficients of a linear model (in the example 3.73 and 25.4) returns a new data set with a column with the values obtained using the corresponding equation. In order for the plugin to comply with the  :ref:`requirements <plugin_requirements>`, one possible definition would be:

.. literalinclude:: ../../../src/plugins/test_plugin_1/__init__.py
   :language: python


