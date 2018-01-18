# -*- coding: UTF-8 -*-#
from __future__ import unicode_literals, print_function

from rest_framework import serializers

from .models import Condition, Action
from workflow.models import Column


class ColumnNameSerializer(serializers.ModelSerializer):

    def create(self, validated_data, **kwargs):
        pass

    class Meta:
        model = Column
        fields = ('name',)


class ConditionSerializer(serializers.ModelSerializer):
    def create(self, validated_data, **kwargs):
        # Bypass create to insert the reference to the action (in context)
        condition_obj = Condition(
            action=self.context['action'],
            name=validated_data['name'],
            description_text=validated_data['description_text'],
            formula=validated_data['formula'],
            is_filter=validated_data['is_filter']
        )

        condition_obj.save()

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
        action_obj = Action(
            workflow=self.context['workflow'],
            name=validated_data['name'],
            description_text=validated_data['description_text'],
            n_selected_rows=validated_data['n_selected_rows'],
            is_out=validated_data['is_out'],
            serve_enabled=validated_data['serve_enabled'],
            active_from=validated_data['active_from'],
            active_to=validated_data['active_to'],
            content=validated_data['content']
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
