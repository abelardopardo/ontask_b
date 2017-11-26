# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import StringIO
import base64
import json

import pandas as pd
from rest_framework import serializers


def df_to_string(df):
    out_file = StringIO.StringIO()
    pd.to_pickle(df, out_file)
    return base64.b64encode(out_file.getvalue())


def string_to_df(value):
    output = StringIO.StringIO()
    output.write(base64.b64decode(value))
    try:
        result = pd.read_pickle(output)
    except Exception:
        return None

    return result


class DataFrameSerializer(serializers.Serializer):
    def to_representation(self, instance):
        # GET
        return instance

    def to_internal_value(self, data):
        # POST / PUT (and then GET to refresh)
        return data


class DataFrameField(serializers.Field):

    def to_representation(self, instance):
        # GET
        return df_to_string(instance)

    def to_internal_value(self, data):
        result = string_to_df(data)
        if result is None:
            raise serializers.ValidationError('Unable to create data frame')

        return result


class DataFramePandasSerializer(serializers.Serializer):

    data_frame = DataFrameField(
        help_text='This field must be the Base64 encoded '
                  'result of the pandas.to_pickle() function'
    )


class DataFrameBasicMergeSerializer(serializers.Serializer):

    how = serializers.CharField(
        required=True,
        initial='',
        help_text='One of the following values: inner, outer, left or right'
    )

    left_on = serializers.CharField(
        required=True,
        initial='',
        help_text='ID of the column in destination data frame with unique key')

    right_on = serializers.CharField(
        required=True,
        initial='',
        help_text='ID of the column in the source data frame with the unique '
                  'key')

    dup_column = serializers.CharField(
        required=False,
        initial='rename',
        help_text='One of the two values: rename (default), or override')


class DataFrameJSONMergeSerializer(serializers.Serializer):

    src_df = DataFrameSerializer()


class DataFramePandasMergeSerializer(serializers.Serializer):

    src_df = DataFrameField(
        help_text='This field must be the Base64 encoded '
                  'result of pandas.to_pickle() function'
    )


