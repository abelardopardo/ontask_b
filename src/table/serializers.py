# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import StringIO
import base64
import json

import pandas as pd
from rest_framework import serializers

from action.serializers import ColumnNameSerializer
from dataops import ops
from .models import View


def df_to_string(df):
    """
    :param df: Pandas dataframe
    :return: Base64 encoded string of its pickled representation
    """
    out_file = StringIO.StringIO()
    pd.to_pickle(df, out_file)
    return base64.b64encode(out_file.getvalue())


def string_to_df(value):
    """
    :param value: Base64 encoded string containing a pickled representation
    of a pandas dataframe
    :return: The encoded dataframe
    """
    output = StringIO.StringIO()
    output.write(base64.b64decode(value))
    try:
        result = pd.read_pickle(output)
    except Exception:
        return None

    return result


class DataFrameJSONField(serializers.Field):
    def to_representation(self, instance):
        # GET
        # Return the to_json result using Pandas. This function though is
        # destructive with respect to NaN and NaT.
        return json.loads(instance.to_json(date_format='iso'))

    def to_internal_value(self, data):
        # POST / PUT (and then GET to refresh)
        try:
            df = pd.DataFrame(data)
            # Detect date/time columns
            df = ops.detect_datetime_columns(df)
        except Exception as e:
            raise serializers.ValidationError(e)

        return df


class DataFrameJSONSerializer(serializers.Serializer):
    data_frame = DataFrameJSONField(
        help_text='JSON string encoding a pandas data frame'
    )


class DataFramePandasField(serializers.Field):
    def to_representation(self, instance):
        # GET
        return df_to_string(instance)

    def to_internal_value(self, data):
        result = string_to_df(data)
        if result is None:
            raise serializers.ValidationError('Unable to create data frame')

        return result


class DataFramePandasSerializer(serializers.Serializer):
    data_frame = DataFramePandasField(
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


class DataFrameJSONMergeSerializer(DataFrameBasicMergeSerializer):
    src_df = DataFrameJSONField(
        help_text='This field must be the JSON string encoding a pandas data '
                  'frame'
    )


class DataFramePandasMergeSerializer(DataFrameBasicMergeSerializer):
    src_df = DataFramePandasField(
        help_text='This field must be the Base64 encoded '
                  'result of pandas.to_pickle() function'
    )


class ViewSerializer(serializers.ModelSerializer):

    # This serializer only includes the column name (the structure is
    # serialized as part of the workflow
    columns = ColumnNameSerializer(required=False, many=True)

    def create(self, validated_data, **kwargs):
        view_obj = View(
            workflow=self.context['workflow'],
            name=validated_data['name'],
            description_text=validated_data['description_text'],
            formula=validated_data['formula']
        )
        view_obj.save()

        # Load the columns in the view
        columns = ColumnNameSerializer(
            data=validated_data.get('columns'),
            many=True,
            required=False,
        )
        if columns.is_valid():
            for citem in columns.data:
                column = view_obj.workflow.columns.get(name=citem['name'])
                view_obj.columns.add(column)
            view_obj.save()
        else:
            view_obj.delete()
            return None

        return view_obj

    class Meta:
        model = View

        exclude = ('id',
                   'workflow',
                   'created',
                   'modified')
