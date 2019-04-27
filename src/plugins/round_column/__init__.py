# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import pandas as pd
import numpy as np

from dataops.plugin import OnTaskPluginAbstract

class_name = 'RoundColumn'


class RoundColumn(OnTaskPluginAbstract):
    """
    Plugin that receives a set of columns of type double and tries to round
    their numbers to a number of decimal places. The parameters are:

    1) List of input columns to round (c1, c2, ..., ck)

    2) number of decimal places
    """

    def __init__(self):

        super().__init__()

        self.name = 'Round column'
        self.description_txt = self.__doc__
        self.input_column_names = list()
        self.output_column_names = list()
        self.parameters = [
            ('Decimal places',
             'integer',
             [],
             2,
             'Number of decimal places to consider'),
        ]

    def run(self, data_frame, parameters=dict):
        """
        Parse the parameters to guarantee that they were correct, and if so,
        returns the dataframe with the rounded columns.

        :param data_frame: Input data for the plugin
        :param parameters: Dictionary with (name, value) pairs.

        :return: a Pandas data_frame to merge with the existing one
        """

        # Check that the number of elements in the coefficients is
        # identical to the number of input columns and they are all doubles.

        # Number of elements in the comma separated list is identical to the
        # number of columns
        decimal_places = parameters.get('Decimal places')
        try:
            decimal_places = int(decimal_places)
        except Exception:
            return 'The decimal places needs to be an integer'

        if decimal_places < 0:
            return 'The decimal places needs to be larger than zero'

        # Loop over columns and verify they have the right type
        for column_name in self.input_column_names:

            if not np.issubdtype(data_frame[column_name], np.number):
                return 'Column {0} has incorrect type'

        # And now perform the rounding
        result_df = pd.DataFrame()
        for column_name in self.input_column_names:

            result_df[column_name + self.output_suffix] = \
                data_frame[column_name].round(decimal_places)

        return result_df
