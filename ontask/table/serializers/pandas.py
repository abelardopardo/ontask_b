# -*- coding: UTF-8 -*-#

"""Functions to serialize pandas data frames."""
import base64
from io import BytesIO
import pickle

from django.utils.translation import ugettext_lazy as _
import pandas as pd
from rest_framework import serializers


class DataFramePandasField(serializers.Field):
    """Serialize a data frame pandas field."""

    def to_representation(self, instance: pd.DataFrame) -> str:
        """Transform the data frame into a string."""
        return df_to_string(instance)

    def to_internal_value(self, string: str) -> pd.DataFrame:
        """Transform string to the DF."""
        data_frame = string_to_df(string)
        if data_frame is None:
            raise serializers.ValidationError(_('Unable to create data frame'))

        return data_frame


class DataFramePandasSerializer(serializers.Serializer):
    """Serializer for a pandas data frame."""

    data_frame = DataFramePandasField(
        help_text=_(
            'This field must be the Base64 encoded result of the '
            + 'pandas.to_pickle() function'),
    )


def df_to_string(df):
    """Transform a data frame into a b64 encoded pickled representation.

    :param df: Pandas dataframe

    :return: Base64 encoded string of its pickled representation
    """
    try:
        out_file = BytesIO()
        pd.to_pickle(df, out_file)
    except ValueError:
        out_file = BytesIO()
        pickle.dump(df, out_file)

    return base64.b64encode(out_file.getvalue())


def string_to_df(string):
    """Transform a pickled b64 encoded string into a data frame.

    :param string: Base64 encoded string containing a pickled representation
    of a pandas dataframe

    :return: The encoded dataframe
    """
    try:
        data_frame = pd.read_pickle(BytesIO(base64.b64decode(string)))
    except ValueError:
        data_frame = pickle.load(
            BytesIO(base64.b64decode(string)),
            encoding='latin1')
    except Exception:
        return None

    return data_frame
