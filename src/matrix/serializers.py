# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import pandas as pd
from rest_framework import serializers


class DataFrameSerializer(serializers.Serializer):
    def to_representation(self, instance):
        # GET
        return instance

    def to_internal_value(self, data):
        # POST / PUT (and then GET to refresh)
        return data

    def create(self, validated_data):
        return pd.DataFrame(validated_data)

    def update(self, instance, validated_data):
        pass


class DataFrameMergeSerializer(serializers.Serializer):
    src_df = DataFrameSerializer()

    how = serializers.CharField(
        required=True,
        initial='',
        help_text='One of the following values: inner, outer, left or right'
    )

    left_on = serializers.CharField(required=True, initial='')

    right_on = serializers.CharField(required=True, initial='')

    dup_column = serializers.CharField(required=False, initial='rename')
