# -*- coding: UTF-8 -*-#
from __future__ import unicode_literals, print_function

from rest_framework import serializers

from .models import Condition, Action


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
        exclude = ('action',)


class ActionSerializer(serializers.ModelSerializer):

    def create(self, validated_data, **kwargs):
        # Bypass create to insert the reference to the workflow (in context)
        action_obj = Action(
            workflow=self.context['workflow'],
            name=validated_data['name'],
            description_text=validated_data['description_text'],
            n_selected_rows=validated_data['n_selected_rows'],
            content=validated_data['content']
        )

        action_obj.save()

        return action_obj

    class Meta:
        model = Action
        fields = ('name', 'description_text', 'n_selected_rows', 'content')


class ActionSerializerDeep(ActionSerializer):

    conditions = ConditionSerializer(required=False, many=True)

    def create(self, validated_data, **kwargs):
        action_obj = Action(
            workflow=self.context['workflow'],
            name=validated_data['name'],
            description_text=validated_data['description_text'],
            n_selected_rows=validated_data['n_selected_rows'],
            content=validated_data['content']
        )

        action_obj.save()

        condition_data = ConditionSerializer(
            data=validated_data.get('conditions', []),
            many=True,
            context={'action': action_obj})
        if condition_data.is_valid():
            condition_data.save()
        return action_obj

    # To get both Actions and Conditions
    class Meta:
        model = Action
        fields = ('name', 'description_text', 'n_selected_rows',
                  'content', 'conditions')
