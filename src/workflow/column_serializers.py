# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from dataops.pandas_db import pandas_datatype_names
from workflow.models import Column


class ColumnSerializer(serializers.ModelSerializer):

    def create(self, validated_data, **kwargs):

        # Preliminary checks
        data_type = validated_data.get('data_type', None)
        if data_type is None or \
                data_type not in pandas_datatype_names.values():
            # The data type is not legal
            raise Exception(_('Incorrect data type {0}.').format(data_type))

        column_obj = None
        try:
            # Create the object, but point to the given workflow
            column_obj = Column(
                name=validated_data['name'],
                description_text=validated_data.get('description_text', ''),
                workflow=self.context['workflow'],
                data_type=data_type,
                is_key=validated_data.get('is_key', False),
                position=validated_data.get('position', 0),
                in_viz=validated_data.get('in_viz', True),
                active_from=validated_data.get('active_from', None),
                active_to=validated_data.get('active_to', None),
            )

            # Set the categories if they exists
            column_obj.set_categories(validated_data.get('categories', []), True)

            if column_obj.active_from and column_obj.active_to and \
                    column_obj.active_from > column_obj.active_to:
                raise Exception(
                    _('Incorrect date/times in the active window for '
                      'column {0}').format(validated_data['name']))

            # All tests passed, proceed to save the object.
            column_obj.save()
        except Exception as e:
            if column_obj:
                column_obj.delete()
            raise e

        return column_obj

    class Meta:
        model = Column
        exclude = ('id', 'workflow')