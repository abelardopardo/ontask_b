# -*- coding: UTF-8 -*-#
from __future__ import unicode_literals, print_function

from rest_framework import serializers

from dataops.formula_evaluation import get_variables
from workflow.models import Column
from .models import Condition, Action


class ColumnNameSerializer(serializers.ModelSerializer):

    def create(self, validated_data, **kwargs):
        pass

    class Meta:
        model = Column
        fields = ('name',)


class ConditionSerializer(serializers.ModelSerializer):
    # The columns field needs a nested serializer because at this point,
    # the column objects must contain only the name (not the entire model).
    # An action is connected to a workflow which has a set of columns
    # attached to it. Thus, the column records are created through the
    # workflow structure, and at this point in the model, only the names are
    # required to then restore the many to many relationship.
    columns = ColumnNameSerializer(required=False, many=True)

    def create(self, validated_data, **kwargs):
        # Bypass create to insert the reference to the action (in context)
        condition_obj = Condition(
            action=self.context['action'],
            name=validated_data['name'],
            description_text=validated_data['description_text'],
            formula=validated_data['formula'],
            n_rows_selected=validated_data.get('n_rows_selected', -1),
            is_filter=validated_data['is_filter'],
        )

        condition_obj.save()

        # Load the columns pointing to the action (if any)
        columns = ColumnNameSerializer(
            data=validated_data.get('columns'),
            many=True,
            required=False,
        )
        if columns.is_valid():
            # Columns have been properly stored. If they are not there,
            # they have to be calculated at the level of the action
            for citem in columns.data:
                column = condition_obj.action.workflow.columns.get(
                    name=citem['name'])
                condition_obj.columns.add(column)

        condition_obj.save()

        if condition_obj.n_rows_selected == -1:
            # Number of rows selected is not up to date, update
            condition_obj.update_n_rows_selected()

        return condition_obj

    class Meta:
        model = Condition
        exclude = ('id', 'action', 'created', 'modified')


class ActionSerializer(serializers.ModelSerializer):
    conditions = ConditionSerializer(required=False, many=True)

    # The columns field needs a nested serializer because at this point,
    # the column objects must contain only the name (not the entire model).
    # An action is connected to a workflow which has a set of columns
    # attached to it. Thus, the column records are created through the
    # workflow structure, and at this point in the model, only the names are
    # required to then restore the many to many relationship.
    columns = ColumnNameSerializer(required=False, many=True)

    def create(self, validated_data, **kwargs):
        # Get content (have to use two names for backward compatibility)
        content = validated_data.get('content', None)
        if not content:
            content = validated_data.get('_content', None)

        action_obj = Action(
            workflow=self.context['workflow'],
            name=validated_data['name'],
            description_text=validated_data['description_text'],
            is_out=validated_data['is_out'],
            serve_enabled=validated_data['serve_enabled'],
            active_from=validated_data['active_from'],
            active_to=validated_data['active_to'],
            content=content
        )

        action_obj.save()

        # Load the conditions pointing to the action
        condition_data = ConditionSerializer(
            data=validated_data.get('conditions', []),
            many=True,
            context={'action': action_obj})
        if condition_data.is_valid():
            condition_data.save()
        else:
            action_obj.delete()
            return None

        # Update the condition variables for each formula if not present
        for condition in action_obj.conditions.all():
            if condition.columns.all().count() == 0:
                col_names = get_variables(condition.formula)
                # Add the corresponding columns to the condition
                condition.columns.set(
                    self.context['workflow'].columns.filter(name__in=col_names)
                )

        # Load the columns pointing to the action (if any)
        columns = ColumnNameSerializer(
            data=validated_data.get('columns'),
            many=True,
            required=False,
        )
        if columns.is_valid():
            for citem in columns.data:
                column = action_obj.workflow.columns.get(name=citem['name'])
                action_obj.columns.add(column)
            action_obj.save()
        else:
            action_obj.delete()
            return None

        return action_obj

    # To get both Actions and Conditions
    class Meta:
        model = Action

        exclude = ('id',
                   'workflow',
                   'created',
                   'modified')