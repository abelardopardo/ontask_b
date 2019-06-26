# -*- coding: utf-8 -*-

"""Serializers to import/export columns and column names."""

from builtins import object

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from ontask.apps.dataops.pandas import pandas_datatype_names
from ontask.apps.workflow.models import Column

try:
    profile  # noqa: Z444
except NameError:
    def profile(bogus_param): return bogus_param  # noqa: E731


class ColumnSerializer(serializers.ModelSerializer):
    """Serialize the entire object."""

    @profile
    def create(self, validated_data, **kwargs):
        """Create a new column."""
        # Preliminary checks
        data_type = validated_data.get('data_type')
        if (
            data_type is None
            or data_type not in list(pandas_datatype_names.values())
        ):
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
                active_from=validated_data.get('active_from'),
                active_to=validated_data.get('active_to'),
            )

            # Set the categories if they exists
            column_obj.set_categories(
                validated_data.get('categories', []),
                True)

            if (
                column_obj.active_from and column_obj.active_to
                and column_obj.active_from > column_obj.active_to
            ):
                raise Exception(
                    _(
                        'Incorrect date/times in the active window for '
                        + 'column {0}').format(validated_data['name']))

            # All tests passed, proceed to save the object.
            column_obj.save()
        except Exception as exc:
            if column_obj:
                column_obj.delete()
            raise exc

        return column_obj

    class Meta(object):
        """Select the model and the fields."""

        model = Column
        exclude = ('id', 'workflow')


class ColumnNameSerializer(serializers.ModelSerializer):
    """Serializer to return only the name."""

    class Meta(object):
        """Select the model and the name."""

        model = Column

        fields = ('name',)
