# -*- coding: utf-8 -*-

from ontask.dataops.plugin import OnTaskTransformation

# The field class_name contains the name of the class to load to execute the
# plugin.
class_name = 'OnTaskTestPlugin'


class OntaskTestPlugin(OnTaskTransformation):
    """
    Example of a class that implements the OnTask plugin interface. The
    objects of this class have to provide the following elements:

    1. Field name: Plugin name show to the users.

    2. Field description_text: A string with the detailed description of what
    the plugin does

    3. Field input_column_names: A potentially empty list of column names 
    (strings). If the list is empty, the columns are selected by the user at
    execution time.

    4. Field output_column_names: List of names (strings) of the
    columns to be used for the output of the transformation. If the list is
    empty, the column names will be taken from the input list with an optional
    suffix to be added.

    5. Field output_column_suffix: (optionally empty) string to add to the name
    of the output columns

    6. Field parameters: an optionally empty list with tuples with the following
    structure:

      ('name', type, [list of allowed values], initial value, help_text)

      These elements will be requested from the user before executing the
      plugin through a form. The conditions on these values are:

      - name must be a string
      - type must be a string equal to "integer", "double", "string", 
        "datetime" or "boolean". 
      - The list of values is to restrict the
        possible values
      - The initial value must be of the type specified by the second 
        element.
      - Help_text a string to show as help text

    7. Method "run" that receives:
       - a pandas data frame with the data to process
       - a string with the name of the key column that will be used to merge
       the result.
       - A dictionary of pairs (name, value) with the parameters described in
       the previous element.

       and returns a result Pandas data frame. This frame **must** have one
       column with the key column name provided so that it can be properly
       merged with the existing data.
    """

    def __init__(self):

        # Call the constructor in the superclass
        super().__init__()

        self.name = 'Plugin Template'
        self.description_text = 'Example of plugin description'
        self.output_column_names = ['RESULT 1', 'RESULT 2']
        self.parameters = [
            ('param string', 'string', ['v1', 'v2'], 'v1', 'help param string'),
            ('param integer', 'integer', [], None, 'help param integer'),
            ('param double', 'double', [1.2, 2.2, 3.2], None,
                             'help param double'),
            ('param boolean', 'boolean', [], True, 'help param boolean'),
            ('param datetime', 'datetime', [], '2018-05-25 18:03:00+09:30',
                               'help param datetime'),
            ('param datetime2', 'datetime', 
                                [],
                                '2018-05-25 18:03:00+09:30',
                                'help param datetime'),
        ]

    def run(self, data_frame, parameters=dict):
        """
        Method to overwrite. Receives a data frame wih a number of columns
        stipulated by the num_column_input pair, the name of a key column and a
        dictionary with parameters of the form name, value.

        Runs the algorithm and returns a pandas data frame structure that is
        merged with the existing data frame in the workflow using the merge_key.

        :param data_frame: Input data for the plugin

        :param parameters: Dictionary with (name, value) pairs.

        :return: a Pandas data_frame to merge with the existing one (must
        contain a column with name merge_key)
        """

        # Extract the key column from the given data frame
        result = data_frame.deep_copy()

        # Process the given data and create the result
        result[self.output_column_names[0]] = 1
        result[self.output_column_names[1]] = 2

        return result
