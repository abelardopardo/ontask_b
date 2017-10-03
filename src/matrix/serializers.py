# -*- coding: UTF-8 -*-#
from __future__ import print_function

from rest_framework import serializers


class MatrixRow(object):

    def __init__(self, **kwargs):
        for cname, cvalue, ctype in zip(
                kwargs.pop('column_names'),
                kwargs.pop('column_values'),
                kwargs.pop('column_types')):
            if ctype == 'string':
                cvalue = str(cvalue)
            elif ctype == 'integer':
                cvalue = int(cvalue)
            elif ctype == 'double':
                cvalue = float(cvalue)
            elif ctype == 'boolean:':
                cvalue = cvalue.lowercase() == 'true'
            else:
                raise Exception('Unable to parse type', ctype)

            setattr(self, cname, cvalue)


class MatrixRowSerializer(serializers.Serializer):
    # A row is a collection of column names, types and values
    col_names = serializers.CharField(required=True, allow_blank=False)
    col_types = serializers.CharField(required=True, allow_blank=False)
    col_values = serializers.CharField(required=True, allow_blank=False)

    def create(self, validated_data):
        """
        Create and return a column row

        :param validated_data: Data received from the outside
        :return: dictionary with the column
        """

        result = []
        for x, y, z in zip(self.col_names, self.col_types, self.col_values):
            if y == 'string':
                z = str(z)
            elif y == 'integer':
                z = int(z)
            elif y == 'double':
                z = float(z)
            elif y == 'boolean':
                z = z.lowercase == 'true'
            else:
                raise Exception('Unable to process type', y)

            result.append((x, z))

        return result

    def update(self, instance, validated_data):
        """
        Update the value
        :param validated_data:
        :return:
        """

        return