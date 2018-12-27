# -*- coding: UTF-8 -*-#


from builtins import object
import datetime

import pytz
from django.utils.translation import ugettext_lazy as _, ugettext
from rest_framework import serializers
from rest_framework.exceptions import APIException
from django.conf import settings
from validate_email import validate_email

from action.models import Action
from dataops.pandas_db import execute_select_on_table
from scheduler.models import ScheduledAction


class ScheduledActionSerializer(serializers.ModelSerializer):
    """
    Serializer to take care of a few fields and the item column
    """
    item_column = serializers.CharField(source='item_column_name',
                                        required=False)

    def instantiate_or_update(self,
                              validated_data,
                              action,
                              execute,
                              item_column,
                              exclude_values,
                              payload,
                              scheduled_obj=None):
        """
        Given the validated data and a set of parameters that have been
        validated, instantiate or update the object of class ScheduledAction.
        :param validated_data: Data obtained by the serializer
        :param action: Action object
        :param execute: Execution date/time
        :param item_column: Item column object (if given)
        :param exclude_values: List of values from item_column to exluce
        :param payload: JSON object
        :param scheduled_obj: Object to instantiate or update
        :return: instantiated object
        """
        if not scheduled_obj:
            scheduled_obj = ScheduledAction()

        scheduled_obj.user = self.context['request'].user
        scheduled_obj.name = validated_data['name']
        scheduled_obj.description_text = validated_data.get('description_text')
        scheduled_obj.action = action
        scheduled_obj.execute = execute
        scheduled_obj.item_column = item_column
        scheduled_obj.exclude_values = exclude_values
        scheduled_obj.payload = payload
        scheduled_obj.status = ScheduledAction.STATUS_PENDING

        scheduled_obj.save()
        return scheduled_obj

    def extra_validation(self, validated_data):
        """
        Checking for extra validation properties in the information contained in
        the validated data. Namely:
        - The action name corresponds with a valid action for the user.
        - The execute time must be in the future
        - The item_column, if present, must be a correct column name
        - Exclude_values must be a list
        - Exclude_values can only be non-empty if item_column is given.
        - The received object has a payload
        :param validated_data:
        :return: action, execute, item_column, exclude_values, payload
        """
        # Get the action
        action = validated_data['action']
        if action.workflow.user != self.context['request'].user:
            # The action could not be found.
            raise APIException(_('Incorrect permission to manipulate action.'))

        # Execution date must be in the future
        execute = validated_data.get('execute', None)
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        if not execute or execute <= now:
            raise APIException(_('Invalid date/time for execution'))

        # Item_column, if present has to be a correct column name
        item_column = validated_data.get('item_column_name')
        if item_column:
            item_column = action.workflow.columns.filter(
                name=item_column
            ).first()
            if not item_column:
                raise APIException(_('Invalid column name for selecting items'))

        exclude_values = validated_data.get('exclude_values')
        # Exclude_values has to be a list
        if exclude_values and not isinstance(exclude_values, list):
            raise APIException(_('Exclude_values must be a list'))

        # Exclude_values can only have content if item_column is given.
        if not item_column and exclude_values:
            raise APIException(_('Exclude items needs a value in item_column'))

        # Check that the received object has a payload
        payload = validated_data.get('payload', {})
        if not payload:
            raise APIException(_('Scheduled objects needs a payload.'))

        return action, execute, item_column, exclude_values, payload

    def create(self, validated_data, **kwargs):

        action, execute, item_column, exclude_values, payload = \
            self.extra_validation(validated_data)

        try:
            scheduled_obj = self.instantiate_or_update(validated_data,
                                                       action,
                                                       execute,
                                                       item_column,
                                                       exclude_values,
                                                       payload)
        except Exception as e:
            raise APIException(
                ugettext('Scheduled action could not be created: {0}').format(
                    e.message)
            )

        return scheduled_obj

    def update(self, instance, validated_data):
        action, execute, item_column, exclude_values, payload = \
            self.extra_validation(validated_data)

        try:
            instance = self.instantiate_or_update(validated_data,
                                                  action,
                                                  execute,
                                                  item_column,
                                                  exclude_values,
                                                  payload,
                                                  instance)

            # Save the object
            instance.save()
        except Exception as e:
            raise APIException(
                ugettext('Unable to update scheduled action: {0}'.format(
                    e.message
                ))
            )

        return instance

    class Meta(object):
        model = ScheduledAction

        fields = ('id', 'name', 'description_text', 'action', 'execute',
                  'item_column', 'exclude_values', 'payload')


class ScheduledEmailSerializer(ScheduledActionSerializer):

    def extra_validation(self, validated_data):

        action, execute, item_column, exclude_values, payload = \
            super(ScheduledEmailSerializer, self).extra_validation(
                validated_data
            )

        if action.action_type != Action.PERSONALIZED_TEXT:
            raise APIException(_('Incorrect type of action to schedule.'))

        subject = payload.get('subject')
        if not subject:
            raise APIException(_('Personalized text needs a subject.'))

        if not item_column:
            raise APIException(_('Personalized text needs a item_column'))

        # Check if the values in the email column are correct emails
        try:
            column_data = execute_select_on_table(
                action.workflow.id,
                [],
                [],
                column_names=[item_column.name])
            if not all([validate_email(x[0]) for x in column_data]):
                # column has incorrect email addresses
                raise APIException(
                    _('The column with email addresses has incorrect values.')
                )
        except TypeError:
            raise APIException(
                _('The column with email addresses has incorrect values.')
            )

        if not all([validate_email(x)
                    for x in payload.get('cc_email', []) if x]):
            raise APIException(
                _('cc_email must be a comma-separated list of emails.')
            )

        if not all([validate_email(x)
                    for x in payload.get('bcc_email', []) if x]):
            raise APIException(
                _('bcc_email must be a comma-separated list of emails.')
            )

        return action, execute, item_column, exclude_values, payload


class ScheduledJSONSerializer(ScheduledActionSerializer):

    def extra_validation(self, validated_data):

        action, execute, item_column, exclude_values, payload = \
            super(ScheduledJSONSerializer, self).extra_validation(
                validated_data
            )

        if action.action_type != Action.PERSONALIZED_JSON:
            raise APIException(_('Incorrect type of action to schedule.'))

        token = payload.get('token')
        if not token:
            raise APIException(_('Personalized JSON needs a token in payload.'))

        return action, execute, item_column, exclude_values, payload
