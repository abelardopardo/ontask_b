"""Serialize the scheduled action."""
from typing import Dict

from django.utils.translation import gettext, gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import APIException

from ontask import get_incorrect_email, models, LOGGER
from ontask.dataops import sql
from ontask.scheduler.services import SCHEDULE_CRUD_FACTORY


class ScheduledOperationSerializer(serializers.ModelSerializer):
    """Serializer to take care of a few fields and the item column."""

    def extra_validation(self, validated_data: Dict):
        """Check for extra properties.

        Checking for extra properties in the information contained in the
        validated data. Namely:

        - The action name corresponds with a valid action for the user.

        - The execute time must be in the future

        - The received object has a payload

        - The item_column, if present, must be a correct column name

        - Exclude_values must be a list

        - Exclude_values can only be non-empty if item_column is given.

        :param validated_data:
        :return: Nothing. Exceptions are raised when anomalies are detected
        """
        this_user = self.context['request'].user

        # Workflow should be owned by the user
        workflow = validated_data['workflow']
        if workflow.user != this_user:
            raise APIException(
                _('Incorrect permission to manipulate workflow'))

        # If action is given, it should be owned by the user
        action = validated_data['action']
        if action is not None and action.workflow != workflow:
            # The action could not be found.
            raise APIException(_('Incorrect permission to manipulate action.'))

        # Execution date/times must be correct
        diagnostic_msg = models.ScheduledOperation.validate_times(
            validated_data.get('execute'),
            validated_data.get('frequency'),
            validated_data.get('execute_until'))
        if diagnostic_msg:
            raise APIException(diagnostic_msg)

        # Check that the received object has a payload
        payload = validated_data.get('payload', {})
        if not payload:
            raise APIException(_('Scheduled objects need a payload.'))

        # Item_column, if present has to be a correct column name
        item_column = payload.get('item_column')
        if item_column:
            item_column = action.workflow.columns.filter(
                name=item_column,
            ).first()
            if not item_column:
                raise APIException(
                    _('Invalid column name for selecting items.'))

        exclude_values = payload.get('exclude_values', [])
        # Exclude_values has to be a list
        if exclude_values is not None and not isinstance(exclude_values, list):
            raise APIException(_('Exclude values must be a list.'))

        # Exclude_values can only have content if item_column is given.
        if not item_column and payload.get('exclude_values'):
            raise APIException(
                _('Exclude items needs a column in item_column.'))

    def create(self, validated_data, **kwargs) -> models.ScheduledOperation:
        """Create a new instance of the scheduled data."""
        del kwargs
        try:
            self.extra_validation(validated_data)
            scheduled_obj = SCHEDULE_CRUD_FACTORY.api_create_or_update(
                self.context['request'].user,
                validated_data)
        except Exception as exc:
            msg = 'Scheduled action could not be created'
            LOGGER.error(msg + ': ' + str(exc))
            raise APIException(gettext(msg))

        return scheduled_obj

    def update(self, instance: models.ScheduledOperation, validated_data):
        """Update the information in the scheduled action."""
        try:
            self.extra_validation(validated_data)
            scheduled_obj = SCHEDULE_CRUD_FACTORY.api_create_or_update(
                self.context['request'].user,
                validated_data,
                instance)
        except Exception as exc:
            msg = 'Unable to update scheduled action.'
            LOGGER.error(msg + ': ' + str(exc))
            raise APIException(gettext(msg))

        return scheduled_obj

    class Meta:
        """Select  model and define fields."""

        model = models.ScheduledOperation

        fields = [
            'id',
            'name',
            'description_text',
            'operation_type',
            'execute',
            'frequency',
            'execute_until',
            'workflow',
            'action',
            'payload']


class ScheduledEmailSerializer(ScheduledOperationSerializer):
    """Validate the presence of certain fields."""

    def extra_validation(self, validated_data: Dict):
        """Validate the presence of certain fields."""
        super().extra_validation(validated_data)

        action = validated_data['action']
        payload = validated_data['payload']
        item_column_name = payload.get('item_column')
        if not item_column_name:
            raise APIException(
                _('Personalized text need a column name in payload '
                  'field item_column.'))

        item_column = action.workflow.columns.filter(
            name=item_column_name).first()
        if not item_column:
            raise APIException(
                _('Incorrect column name in field item_column.'))

        if action.action_type != models.Action.PERSONALIZED_TEXT:
            raise APIException(_('Incorrect type of action to schedule.'))

        subject = payload.get('subject')
        if not subject:
            raise APIException(_('Personalized text needs a subject.'))

        # Check if the values in the email column are correct emails
        try:
            column_data = sql.get_rows(
                action.workflow.get_data_frame_table_name(),
                column_names=[item_column.name])
            incorrect_email = get_incorrect_email(
                [row[item_column.name] for row in column_data])
            if incorrect_email:
                # column has incorrect email addresses
                raise APIException(
                    _('Incorrect email value "{0}".').format(incorrect_email))
        except TypeError:
            raise APIException(
                _('The column with email addresses has incorrect values.'))
        payload['item_column'] = item_column.id

        try:
            incorrect_email = get_incorrect_email(
                [email for email in payload.get('cc_email', '').split()
                 if email])
            if incorrect_email:
                raise APIException(
                    _('Incorrect email value "{0}".').format(incorrect_email))
        except Exception:
            raise APIException(
                _('cc_email must be a space-separated list of emails.'))

        try:
            incorrect_email = get_incorrect_email(
                [email for email in payload.get('bcc_email', '').split()
                 if email])
            if incorrect_email:
                raise APIException(
                    _('Incorrect email value "{0}".').format(incorrect_email))
        except Exception:
            raise APIException(
                _('bcc_email must be a space-separated list of emails.'))


class ScheduledJSONSerializer(ScheduledOperationSerializer):
    """Class to add an extra check for the presence of a token."""

    def extra_validation(self, validated_data):
        """Check that the token is present before execution."""
        super().extra_validation(validated_data)

        action = validated_data['action']
        if action.action_type != models.Action.PERSONALIZED_JSON:
            raise APIException(_('Incorrect type of action to schedule.'))

        payload = validated_data['payload']
        item_column_name = payload.get('item_column')
        if not item_column_name:
            raise APIException(
                _('Personalized text need a column name in payload '
                  'field item_column.'))

        item_column = action.workflow.columns.filter(
            name=item_column_name).first()
        if not item_column:
            raise APIException(
                _('Incorrect column name in field item_column.'))
        payload['item_column'] = item_column.id

        if not payload.get('token'):
            raise APIException(_(
                'Personalized JSON needs a token in payload.'))
