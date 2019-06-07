# -*- coding: utf-8 -*-

"""View serializer."""
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from table.models import View
from workflow.serialize_column import ColumnNameSerializer


class ViewSerializer(serializers.ModelSerializer):
    """Serializer for the View.

    This serializer only includes the column name (the structure is
    serialized as part of the workflow
    """

    columns = ColumnNameSerializer(required=False, many=True)

    def create(self, validated_data, **kwargs):
        """Create the View object."""
        view_obj = None
        try:
            view_obj = View(
                workflow=self.context['workflow'],
                name=validated_data['name'],
                description_text=validated_data['description_text'],
                formula=validated_data['formula'],
            )
            view_obj.save()

            # Load the columns in the view
            columns = ColumnNameSerializer(
                data=validated_data.get('columns'),
                many=True,
                required=False,
            )
            if columns.is_valid():
                view_column_names = [col['name'] for col in columns.data]
                view_obj.columns.set([
                    col for col in self.context['columns']
                    if col.name in view_column_names
                ])
                view_obj.save()
            else:
                raise Exception(_('Incorrect column data'))

        except Exception:
            if view_obj and view_obj.id:
                view_obj.delete()
            raise

        return view_obj

    class Meta(object):
        """Set the model and fields to exclude."""

        model = View

        exclude = (
            'id',
            'workflow',
            'created',
            'modified')
