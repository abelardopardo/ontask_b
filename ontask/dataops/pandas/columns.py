# -*- coding: utf-8 -*-

"""Data types considered in OnTask and its relation with Pandas data types"""
from typing import Dict, List

import pandas as pd

from ontask.dataops.pandas.datatypes import pandas_datatype_names


def get_column_statistics(df_column) -> Dict:
    """Calculate a set of statistics or a DataFrame column.

    Given a data frame with a single column, return a set of statistics
    depending on its type.

    :param df_column: data frame with a single column
    :return: A dictionary with keys depending on the type of column
      {'min': minimum value (integer, double an datetime),
       'q1': Q1 value (0.25) (integer, double),
       'mean': mean value (integer, double),
       'median': median value (integer, double),
       'mean': mean value (integer, double),
       'q3': Q3 value (0.75) (integer, double),
       'max': maximum value (integer, double an datetime),
       'std': standard deviation (integer, double),
       'counts': (integer, double, string, datetime, Boolean',
       'mode': (integer, double, string, datetime, Boolean,
       or None if the column has all its values to NaN
    """
    if len(df_column.loc[df_column.notnull()]) == 0:
        # The column has no data
        return None

    # Dictionary to return
    to_return = {
        'min': 0,
        'q1': 0,
        'mean': 0,
        'median': 0,
        'q3': 0,
        'max': 0,
        'std': 0,
        'mode': None,
        'counts': {},
    }

    data_type = pandas_datatype_names.get(df_column.dtype.name)

    if data_type == 'integer' or data_type == 'double':
        quantiles = df_column.quantile([0, .25, .5, .75, 1])
        to_return['min'] = '{0:g}'.format(quantiles[0])
        to_return['q1'] = '{0:g}'.format(quantiles[.25])
        to_return['mean'] = '{0:g}'.format(df_column.mean())
        to_return['median'] = '{0:g}'.format(quantiles[.5])
        to_return['q3'] = '{0:g}'.format(quantiles[.75])
        to_return['max'] = '{0:g}'.format(quantiles[1])
        to_return['std'] = '{0:g}'.format(df_column.std())

    to_return['counts'] = df_column.value_counts().to_dict()
    mode = df_column.mode()
    if len(mode) == 0:
        mode = '--'
    to_return['mode'] = mode[0]

    return to_return


def is_unique_column(df_column: pd.Series) -> bool:
    """Check if a column has unique non-empty values.

    :param df_column: Column of a pandas data frame
    :return: Boolean encoding if the column has unique values
    """
    return len(df_column.dropna().unique()) == len(df_column)


def are_unique_columns(data_frame: pd.DataFrame) -> List[bool]:
    """Check if columns have unique non-empty values.

    :param data_frame: Pandas data frame
    :return: Array of Booleans stating of a column has unique values
    """
    return [
        is_unique_column(data_frame[col]) for col in list(data_frame.columns)
    ]


def has_unique_column(data_frame: pd.DataFrame) -> bool:
    """Verify if the data frame has a unique column.

    :param data_frame:
    :return: Boolean with the result
    """
    return any(
        is_unique_column(data_frame[col]) for col in data_frame.columns
    )


def detect_datetime_columns(data_frame: pd.DataFrame) -> pd.DataFrame:
    """Try to convert columns to datetime type.

    Given a data frame traverse the columns and those that have type "string"
    try to see if it is of type datetime. If so, apply the translation.

    :param data_frame: Pandas dataframe to detect datetime columns
    :return: The modified data frame
    """
    # Strip white space from all string columns and try to convert to
    # datetime just in case
    for column in list(data_frame.columns):
        if data_frame[column].dtype.name == 'object':
            # Column is a string!
            data_frame[column] = data_frame[column].str.strip()

            # Try the datetime conversion
            try:
                series = pd.to_datetime(
                    data_frame[column],
                    infer_datetime_format=True)
                # Datetime conversion worked! Update the data_frame
                data_frame[column] = series
            except ValueError:
                pass

    return data_frame
