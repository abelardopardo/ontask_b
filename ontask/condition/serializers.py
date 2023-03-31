# -*- coding: UTF-8 -*-#

"""Classes to serialize Conditions."""
from typing import Dict

from rest_framework import serializers

from ontask import models
from ontask.column.serializers import ColumnNameSerializer
from ontask.core import OnTaskObjectIdField

try:
    profile  # noqa: Z444
except NameError:
    def profile(bogus: int) -> int:
        """Useless, to prevent an emtpy exception handler"""
        return bogus  # noqa E731


class ConditionBaseSerializer(serializers.ModelSerializer):
    """Class to serialize a Condition."""

    # The columns field needs a nested serializer because at this point,
    # the column objects must contain only the name (not the entire model).
    # An action is connected to a workflow which has a set of columns
    # attached to it. Thus, the column records are created through the
    # workflow structure, and at this point in the model, only the names are
    # required to restore the many to many relationship.
    columns = ColumnNameSerializer(required=False, many=True)

    @staticmethod
    def set_columns(
        cond_obj: models.ConditionBase,
        columns_data: Dict
    ):
        """Set the column information in the condition/filter object.

        :param cond_obj: Condition/Filter object
        :param columns_data: Serialized column name information
        :return: Nothing. Side effects on the object
        """
        # Set the columns in the condition
        col_names = [c_data['name'] for c_data in columns_data]
        cond_obj.columns.set(
            cond_obj.workflow.columns.filter(name__in=col_names))

        # Save condition object
        cond_obj.save()

    class Meta:
        """Define object condition and select fields to serialize."""

        abstract = True
        exclude = [
            'id',
            'workflow',
            'action',
            'created',
            'modified',
            '_formula_text']


class ConditionSerializer(ConditionBaseSerializer):

    @staticmethod
    def create_condition(
        validated_data,
        context: Dict
    ) -> models.Condition:
        """Create a new condition with the validated data.

        :param validated_data: Dictionary with the data validated by the
        serializer
        :param context: Dictionary with context information
        :return: new condition object
        """
        columns_data = validated_data.pop('columns', [])
        workflow = context['workflow']

        condition_obj = models.Condition.objects.create(
            workflow=workflow,
            action=context['action'],
            **validated_data)

        ConditionBaseSerializer.set_columns(condition_obj, columns_data)

        return condition_obj

    class Meta(ConditionBaseSerializer.Meta):
        """Define object condition and select fields to serialize."""

        model = models.Condition


class FilterSerializer(ConditionBaseSerializer):

    object_id = OnTaskObjectIdField(required=False)

    @staticmethod
    def create_filter(
        validated_data: Dict,
        context: Dict
    ) -> models.Filter:
        """Create a new filter with the validated data.

        :param validated_data: Dictionary with the data validated by the
        serializer
        :param context: Dictionary with context information
        :return: new Filter object
        """
        columns_data = validated_data.pop('columns', [])
        workflow = context['workflow']

        filter_map = context['filter_map']
        filter_id = validated_data.pop('object_id', None)
        filter_obj = filter_map.get(filter_id)
        if filter_obj:
            return filter_obj

        filter_obj = models.Filter.objects.create(
            workflow=workflow,
            action=context.get('action'),
            view=context.get('view'),
            **validated_data)
        if filter_id is not None:
            filter_map[filter_id] = filter_obj

        ConditionBaseSerializer.set_columns(filter_obj, columns_data)

        return filter_obj

    class Meta(ConditionBaseSerializer.Meta):
        """Define object condition and select fields to serialize."""

        model = models.Filter

        exclude = [
            'id',
            'workflow',
            'created',
            'modified',
            '_formula_text']


class ConditionNameSerializer(serializers.ModelSerializer):
    """Trivial serializer to dump only the name of the column."""

    class Meta:
        """Select the model and the only field required."""

        model = models.Condition
        fields = ['name']
