# -*- coding: UTF-8 -*-#

"""Serialize the scheduled action."""

import datetime
from builtins import object

import pytz
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import APIException

from action.models import Action
from dataops.sql.row_queries import get_rows
from ontask import is_correct_email
from scheduler.models import ScheduledAction


class ScheduledActionSerializer(serializers.ModelSerializer):
    """Serializer to take care of a few fields and the item column."""

    item_column = serializers.CharField(
        source='item_column_name',
        required=False)

    def instantiate_or_update(
        self,
        validated_data,
        action,
        execute,
        item_column,
        exclude_values,
        payload,
        scheduled_obj=None,
    ):
        """Instantiate or update the object of class ScheduledAction.

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
        """Check for extra properties.

        Checking for extra validation properties in the information contained
        in the validated data. Namely:

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
        execute = validated_data.get('execute')
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        if not execute or execute <= now:
            raise APIException(_('Invalid date/time for execution'))

        # Item_column, if present has to be a correct column name
        item_column = validated_data.get('item_column_name')
        if item_column:
            item_column = action.workflow.columns.filter(
                name=item_column,
            ).first()
            if not item_column:
                raise APIException(
                    _('Invalid column name for selecting items'))

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
        """Create a new instance of the scheduled data."""
        act, execute, column, exclude, payload = self.extra_validation(
            validated_data)

        try:
            scheduled_obj = self.instantiate_or_update(
                validated_data,
                act,
                execute,
                column,
                exclude,
                payload)
        except Exception as exc:
            raise APIException(
                ugettext('Scheduled action could not be created: {0}').format(
                    str(exc)))

        return scheduled_obj

    def update(self, instance, validated_data):
        """Update the information in the scheduled action."""
        act, execute, column, exclude, payload = self.extra_validation(
            validated_data)

        try:
            instance = self.instantiate_or_update(
                validated_data,
                act,
                execute,
                column,
                exclude,
                payload,
                instance)

            # Save the object
            instance.save()
        except Exception as exc:
            raise APIException(
                ugettext('Unable to update scheduled action: {0}').format(
                    str(exc)))

        return instance

    class Meta(object):
        """Select  model and define fields."""

        model = ScheduledAction

        fields = (
            'id',
            'name',
            'description_text',
            'action',
            'execute',
            'item_column',
            'exclude_values',
            'payload')


class ScheduledEmailSerializer(ScheduledActionSerializer):
    """Validate the presence of certain fields."""

    def extra_validation(self, validated_data):
        """Validate the presence of certain fields."""
        act, execute, column, exclude, payload = super().extra_validation(
            validated_data)

        if act.action_type != Action.personalized_text:
            raise APIException(_('Incorrect type of action to schedule.'))

        subject = payload.get('subject')
        if not subject:
            raise APIException(_('Personalized text needs a subject.'))

        if not column:
            raise APIException(_('Personalized text needs a item_column'))

        # Check if the values in the email column are correct emails
        try:
            column_data = get_rows(
                act.workflow.get_data_frame_table_name(),
                column_names=[column.name])
            if not all(is_correct_email(email) for __, email in column_data):
                # column has incorrect email addresses
                raise APIException(
                    _('The column with email addresses has incorrect values.'))
        except TypeError:
            raise APIException(
                _('The column with email addresses has incorrect values.'))

        if not all(
            is_correct_email(email_val)
            for email_val in payload.get('cc_email', [])
            if email_val
        ):
            raise APIException(
                _('cc_email must be a comma-separated list of emails.'))

        if not all(
            is_correct_email(email)
            for email in payload.get('bcc_email', []) if email
        ):
            raise APIException(
                _('bcc_email must be a comma-separated list of emails.'))

        return act, execute, column, exclude, payload


class ScheduledJSONSerializer(ScheduledActionSerializer):
    """Class to add an extra check for the presence of a token."""

    def extra_validation(self, validated_data):
        """Check that the token is present before execution."""
        act, execute, column, exclude, pload = super().extra_validation(
            validated_data)

        if act.action_type != Action.personalized_json:
            raise APIException(_('Incorrect type of action to schedule.'))

        if not pload.get('token'):
            raise APIException(_(
                'Personalized JSON needs a token in payload.'))

        return act, execute, column, exclude, pload
