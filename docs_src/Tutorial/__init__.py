# -*- coding: utf-8 -*-

import pandas as pd

# The field class_name contains the name of the class to load to execute the
# plugin.
class_name = 'LinearRegressionModel'


class LinearRegressionModel:
    """
    Class implementing an OnTask plugin that given two coefficients it
    applies a linear regression model to the input column.
    """

    def __init__(self):
        self.name = 'Linear Regression Predictive Model'
        self.description_text = """
        Given a column and the coefficients A and B, it computes the linear 
        model Ax + B, where x is obtained from the input column.
        """
        self.input_column_names = list()
        self.output_column_names = ['Linear Model']
        self.parameters = [
            ('A', 'double', [], 0.0, 'Linear coefficient'),
            ('B', 'double', [], 0.0, 'Constant coefficient'),
        ]

    def run(self, data_frame, merge_key, parameters=None):
        """
        :param data_frame: Input data for the plugin
        :param merge_key: Name of the column key that will be used for merging
        :param parameters: Dictionary with (name, value) pairs.

        :return: a Pandas data_frame to merge with the existing one (must
        contain a column with name merge_key)
        """

        # Extract the key column from the given data frame
        result = pd.DataFrame(data_frame[merge_key])

        # Process the given data and create the result
        result[self.output_column_names[0]] = \
            parameters['A'] * data_frame[self.input_column_names[0]] + \
            parameters['B']

        return result
