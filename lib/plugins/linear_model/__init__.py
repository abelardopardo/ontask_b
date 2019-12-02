# -*- coding: utf-8 -*-

import pandas as pd

from ontask.dataops.plugin import OnTaskModel

class_name = 'LinearModel'


class LinearModel(OnTaskModel):
    """Plugin to execute the linear model y = 3.73 * Contribution + 25.4

    The result is stored in column 'Final Exam Predict'
    """

    def __init__(self):
        """Initialize all the fields."""
        super().__init__()
        self.name = 'Linear Model'
        self.description_text = "Obtain a prediction of the final exam score."
        self.input_column_names = ['Contribution']
        self.output_column_names = ['Final Exam Predict']

    def run(self, data_frame, parameters=dict):
        """
        Parse the parameters to guarantee that they were correct, and if so,
        returns the dataframe with the resulting linear model.

        :param data_frame: Input data for the plugin
        :param parameters: Dictionary with (name, value) pairs.
        :return: a Pandas data_frame to merge with the existing one 
        """

        new_dataframe = pd.DataFrame(3.73 * data_frame['Contribution'] + 25.4)
        new_dataframe.columns = self.output_column_names

        return new_dataframe
