# -*- coding: UTF-8 -*-#
from __future__ import unicode_literals, print_function

from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

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
    # required to restore the many to many relationship.
    columns = ColumnNameSerializer(required=False, many=True)

    def create(self, validated_data, **kwargs):
        condition_obj = None

        try:
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

            if validated_data.get('columns'):
                # Load the columns pointing to the action (if any)
                columns = ColumnNameSerializer(
                    data=validated_data.get('columns'),
                    many=True,
                    required=False,
                )
                if columns.is_valid():
                    cnames = [c['name'] for c in columns.data]
                else:
                    raise Exception(_('Incorrect column data'))
            else:
                cnames = get_variables(condition_obj.formula)

            # Set the condition values
            condition_obj.columns.set(
                condition_obj.action.workflow.columns.filter(name__in=cnames)
            )

            # Save condition object
            condition_obj.save()

            if condition_obj.n_rows_selected == -1:
                # Number of rows selected is not up to date, update
                condition_obj.update_n_rows_selected()
        except Exception:
            if condition_obj and condition_obj.id:
                condition_obj.delete()
            raise

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
        action_obj = None
        try:
            action_obj = Action(
                workflow=self.context['workflow'],
                name=validated_data['name'],
                description_text=validated_data['description_text'],
                is_out=validated_data['is_out'],
                serve_enabled=validated_data['serve_enabled'],
                active_from=validated_data['active_from'],
                active_to=validated_data['active_to'],
                content=validated_data.get('content', None)
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
                raise Exception(_('Invalid condition data'))

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
                raise Exception(_('Invalid column data'))
        except Exception:
            if action_obj and action_obj.id:
                action_obj.delete()
            raise

        return action_obj

    # To get both Actions and Conditions
    class Meta:
        model = Action

        exclude = ('id',
                   'workflow',
                   'created',
                   'modified')
