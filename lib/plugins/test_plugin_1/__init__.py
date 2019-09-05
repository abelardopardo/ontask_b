# -*- coding: utf-8 -*-

import pandas as pd

from ontask.dataops.plugin import OnTaskTransformation

# This field class_name contains the name of the class to load to execute the
# plugin.
class_name = 'OnTaskTestPlugin'

# The class must have the name stored in the previous field and must inherit
# from OnTaskPluginAbstract


class OnTaskTestPlugin(OnTaskTransformation):
    """
    Example of a class that implements the OnTask plugin interface. The
    class has to satisfy the following properties:

    - Class defined in the file __init__.py in its own folder (Python module)

    - The file must have the field with name "class_name" containing the name
      of the class implementing the plugin (allows for multiple classes to be
      defined in the same file.

    - The class implementing the plugin must inherit from OnTaskPluginAbstract

    - The class must have a non-empty doc string (like this one) explaining
      in detail the operations implemented by the plugin

    - The objects of the class must have the following fields:

      - name (string): Plugin name show to the users.

      - description_text (sting): A string with a brief description of what
        the plugin does

      - input_column_names (list of strings): A potentially empty list of column
        names. If the list is empty, OnTask will allow the user to specify any
        arbitrary set of columns. If the list is not empty, the user will be
        required to provide a list with names of existing columns to map to the
        inputs to the plugin.

      - output_column_names (list of strings): List of names (strings) to use as
        column names for the result of the calculations.

      - parameters (list of tuples): an optionally empty list with tuples with
        the following structure:

        ('name', type, [list of allowed values], initial value, help_text)

        These elements will be requested from the user before executing the
        plugin through a form. The values in the tuple must satisfy the
        following conditions:

        - name must be a string

        - type must be a string equal to "integer", "double", "string",
          "datetime" or "boolean".

        - The list of values is to restrict the possible values for this
          parameter.

        - The initial value must be of the type specified by the second
          element.

        - Help_text a string to show as help text

    - The class must implement the method "run" that receives:
       - a pandas data frame with the data to process
       - A dictionary of pairs (name, value) with the parameters previously
         described.

    - The method run must return a result data frame that will be merged with
      the existing data. The order of the rows will be assumed to be identical
      than the existing data frame.
    """

    def __init__(self):

        super().__init__()

        # Short name shown to the user
        self.name = 'Test Plugin 1 Name'
        # Brief description
        self.description_text = 'Create two extra columns with constants 1 and 2'
        # Allows the user to provide any non-empty subset of column names
        self.input_column_names = list()
        # Names of the result columns
        self.output_column_names = ['RESULT 1', 'RESULT 2']
        # Example of how to use the parameters field (not used)
        self.parameters = [
            ('param string', 'string', [
             'v1', 'v2'], 'v1', 'help param string'),
            ('param integer', 'integer', [], None, 'help param integer'),
            ('param double',
             'double',
             [1.2, 2.2, 3.2],
             None,
             'help param double'),
            ('param boolean', 'boolean', [], True, 'help param boolean'),
            ('param datetime',
             'datetime',
             [],
             '2018-05-25 18:03:00+09:30',
             'help param datetime'),
            ('param datetime2',
             'datetime',
             [],
             '2018-05-25 18:03:00+09:30',
             'help param datetime'),
        ]

    def run(self, data_frame, parameters=dict):
        """
        Method to overwrite. Receives a data frame wih a number of columns
        stipulated by the num_column_input pair and a dictionary with parameters
        of the form name, value.

        Runs the algorithm and returns a pandas data frame structure that is
        merged with the existing data frame in the workflow

        :param data_frame: Input data for the plugin
        :param parameters: Dictionary with (name, value) pairs.

        :return: a Pandas data_frame to merge with the existing one
        """

        # Create the result
        result = pd.DataFrame()

        # Process the given data and create the result
        result[self.output_column_names[0]] = \
            [1 for _ in range(data_frame.shape[0])]
        result[self.output_column_names[1]] = \
            [2 for _ in range(data_frame.shape[0])]

        return result
