# -*- coding: UTF-8 -*-#
from __future__ import print_function

from rest_framework import serializers


class MatrixUniqueTriplet(object):

    def __init__(self, **kwargs):
        for field in ('name', 'type', 'value'):
            setattr(self, field, kwargs.get(field, None))


class MatrixUniqueTripletSerializer(serializers.Serializer):

    # A triplet of (name, value, type) all represented as strings
    name = serializers.CharField(max_length=256, allow_blank=False)
    value = serializers.CharField(max_length=256, allow_blank=False)
    type = serializers.CharField(max_length=256, allow_blank=True)

    # Method that
    def create(self, validated_data):
        """
        Create and return a triplet

        :param validated_data: Data received from the outside
        :return: create new element
        """
        return MatrixUniqueTriplet(**validated_data)

    def update(self, instance, validated_data):
        """
        Update the value
        :param validated_data:
        :return:
        """

        instance.name = validated_data['name']
        instance.type = validated_data['type']
        instance.value = validated_data.get('value', None)
        return instance


class MatrixCell(object):

    def __init__(self, **kwargs):
        # Set the unique triplet
        self.uni_triplet = MatrixUniqueTriplet(
            name=kwargs['uniq'].name,
            value=kwargs['uniq'].value,
            type=kwargs['uniq'].type
        )

        self.col_triplet = MatrixUniqueTriplet(
            name=kwargs['col'].name,
            value=kwargs['col'].value,
            type=kwargs['col'].type
        )

        # And the cell value
        self.cell_value = kwargs.get('cell_value', None)


class MatrixCellSerializer(serializers.Serializer):
    uni_triplet = MatrixUniqueTripletSerializer()
    col_triplet = MatrixUniqueTripletSerializer()
    cell_value = serializers.CharField(max_length=512, allow_blank=True)

    def create(self, validated_data):
        return MatrixCell(**validated_data)

    def update(self, instance, validated_data):
        instance.uni_triplet = MatrixUniqueTriplet(
            name=validated_data.uni_triplet.name,
            value=validated_data.uni_triplet.value,
            type=validated_data.uni_triplet.type)

        instance.col_triplet = MatrixUniqueTriplet(
            name=validated_data.col_triplet.name,
            value=validated_data.col_triplet.value,
            type=validated_data.col_triplet.type)

        instance.cell_value = validated_data.get('cell_value', None)

        return instance

# class MatrixRow(object):
#
#     uniq_name = serializers.CharField
#     def __init__(self, **kwargs):
#         for field in ('key', 'value'):
#             setattr(self, field, kwargs.get(field, None))
#
#
# class MatrixRowSerializer(serializers.Serializer):
#     # A row is a collection of column names, types and values
#     key = serializers.CharField(max_length=256)
#     value = serializers.CharField(max_length=256)
#
#     def create(self, validated_data):
#         """
#         Create and return a column row
#
#         :param validated_data: Data received from the outside
#         :return: dictionary with the column
#         """
#         return MatrixRow(**validated_data)
#
#     def update(self, instance, validated_data):
#         """
#         Update the value
#         :param validated_data:
#         :return:
#         """
#
#         for field, value in validated_data.items():
#             setattr(instance, field, value)
#         return instance

# m1 = MatrixUniqueTriplet(name='n1', value='12', type='integer')
# m2 = MatrixUniqueTriplet(name='n2', value='14', type='integer')
# url = 'http://127.0.0.1:8000' + reverse('matrix:getpost_cell', kwargs={
# 'pk':26})
# payload = '{"uni_triplet":{"name":"SID","value":"386719553","type":"integer"},"col_triplet":{"name":"n2","value":"14","type":"integer"},"cell_value":"12"}'
# headers = {'content-type': 'application/json'}
# response = requests.post(url, data=json.dumps(payload), headers=headers)