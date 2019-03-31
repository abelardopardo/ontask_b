# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import pandas as pd
import numpy as np

class_name = 'RoundColumn'


class RoundColumn(object):
    """
    Plugin that receives a set of columns of type double and tries to round
    their numbers to a number of decimal places. The parameters are:

    1) List of input columns to round (c1, c2, ..., ck)

    2) number of decimal places

    """

    def __init__(self):
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

    def run(self, data_frame, merge_key, parameters=dict):
        """
        Parse the parameters to guarantee that they were correct, and if so,
        returns the dataframe with the rounded columns.

        :param data_frame: Input data for the plugin
        :param merge_key: Name of the column key that will be used for merging
        :param parameters: Dictionary with (name, value) pairs.

        :return: a Pandas data_frame to merge with the existing one (must
        contain a column with name merge_key)
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
            if column_name == merge_key:
                # Skip the merge key
                continue

            if not np.issubdtype(data_frame[column_name], np.number):
                return 'Column {0} has incorrect type'

        # And now perform the rounding
        for column_name in self.input_column_names:

            data_frame.update(
                data_frame[column_name].round(decimal_places),
                join='left',
                overwrite=True
            )
            # Add the column name to the output column name
            self.output_column_names.append(column_name)

        return data_frame
