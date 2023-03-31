# -*- coding: utf-8 -*-

"""Serializers to import/export columns and column names."""
from typing import Dict, Optional

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from ontask import models
from ontask.dataops import pandas, sql

try:
    profile  # noqa: Z444
except NameError:
    def profile(bogus_param: int) -> int: return bogus_param  # noqa: E731


class ColumnSerializer(serializers.ModelSerializer):
    """Serialize the entire object."""

    @staticmethod
    def create_column(
        validated_data: Dict,
        context: Dict
    ) -> Optional[models.Condition]:
        """Create the new object based on the validated data"""
        workflow = context['workflow']
        column = models.Column.objects.create(
            workflow=workflow,
            **validated_data)

        if (
            column.active_from and column.active_to
            and column.active_from > column.active_to
        ):
            raise Exception(
                _(
                    'Incorrect date/times in the active window for '
                    + 'column {0}').format(validated_data['name']))

        column.set_categories(
            validated_data.get('categories', []),
            validate=True,
            update=False)

        if not context.get('add_to_df_table', False):
            return column

        sql.add_column_to_db(
            workflow.get_data_frame_table_name(),
            column.name,
            column.data_type)

        # Update the column position and count in the workflow
        workflow.ncols = workflow.ncols + 1
        workflow.save(update_fields=['ncols'])

        column.position = workflow.ncols
        column.save(update_fields=['position'])

        return column

    class Meta:
        """Select the model and the fields."""

        model = models.Column
        exclude = ['id', 'workflow']


class ColumnNameSerializer(serializers.ModelSerializer):
    """Serializer to return only the name."""

    class Meta:
        """Select the model and the name."""

        model = models.Column
        fields = ['name']
