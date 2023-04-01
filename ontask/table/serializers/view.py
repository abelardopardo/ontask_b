"""View serializer."""
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from ontask import models
from ontask.core import OnTaskObjectIdField
from ontask.condition.serializers import FilterSerializer, ColumnNameSerializer


class ViewSerializer(serializers.ModelSerializer):
    """Serializer for the View.

    This serializer only includes the column name (the structure is
    serialized as part of the workflow
    """

    columns = ColumnNameSerializer(required=False, many=True)

    filter = FilterSerializer(required=False, many=False, allow_null=True)

    @staticmethod
    def create_view(validated_data, context) -> models.View:
        workflow = context['workflow']
        columns_data = validated_data.pop('columns', [])
        filter_data = validated_data.pop('filter', None)

        if workflow.views.filter(name=validated_data['name']).exists():
            raise Exception(_(
                'View with name {0} already exists').format(
                validated_data['name']))

        view_obj = models.View.objects.create(
            workflow=workflow,
            **validated_data)

        columns = []
        for c_data in columns_data:
            column = workflow.columns.filter(name=c_data['name']).first()
            if column is None:
                raise Exception(_('Invalid column name {0}').format(
                    c_data['name']))
            columns.append(column)
        view_obj.columns.set(columns)

        if filter_data:
            view_obj.filter = FilterSerializer.create_filter(
                filter_data,
                context)

        view_obj.save()

        return view_obj

    class Meta:
        """Set the model and fields to exclude."""

        model = models.View
        exclude = ['id', 'workflow', 'created', 'modified']


class ViewNameSerializer(serializers.ModelSerializer):
    """Trivial serializer to dump only the name of the view."""

    class Meta:
        """Select the model and the only field required."""

        model = models.View
        fields = ['name']
