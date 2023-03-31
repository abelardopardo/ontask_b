# -*- coding: UTF-8 -*-#

"""Serializers to import/export, list the workflows."""
from builtins import str
from typing import List

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import APIException

from ontask import models, core
from ontask.action.serializers import ActionSerializer
from ontask.column.serializers import ColumnSerializer
from ontask.dataops import pandas
from ontask.table.serializers import DataFramePandasField, ViewSerializer

try:
    profile  # noqa: Z444
except NameError:
    def profile(bogus: int) -> int: return bogus  # noqa: E731


class WorkflowListSerializer(serializers.ModelSerializer):
    """Workflow List serializer to use with the API."""

    def create(self, validated_data, **kwargs):
        """Create the new object."""
        attributes = validated_data.get('attributes', {})
        if not isinstance(attributes, dict):
            raise APIException(_(
                'Attributes must be a dictionary of (string, string) pairs.'))

        if any(
            not isinstance(key, str) or not isinstance(aval, str)
            for key, aval in list(attributes.items())
        ):
            raise APIException(_('Attributes must be a dictionary (str, str)'))

        workflow_obj = None
        try:
            workflow_obj = models.Workflow(
                user=self.context['request'].user,
                name=validated_data['name'],
                description_text=validated_data.get('description_text', ''),
                nrows=0,
                ncols=0,
                attributes=attributes,
            )

            workflow_obj.save()
        except Exception:
            if workflow_obj and workflow_obj.id:
                workflow_obj.delete()
            raise APIException(_('Workflow could not be created.'))

        return workflow_obj

    class Meta:
        """Select model and fields to consider."""

        model = models.Workflow
        fields = ['id', 'name', 'description_text', 'attributes']


class WorkflowExportSerializer(serializers.ModelSerializer):
    """Serializer to export the workflow.

    This serializer is use to export Workflows selecting a subset of actions.
    Since the SerializerMethodField used for the selection is a read_only
    field, the import is managed by a different serializer that uses a
    regular one for the action field (see WorkflowImportSerializer)
    """

    data_frame = DataFramePandasField(
        required=False,
        allow_null=True,
        help_text=_(
            'This field must be the Base64 encoded '
            + 'result of pandas.to_pickle() function'),
    )

    columns = ColumnSerializer(many=True, required=False)

    actions = serializers.SerializerMethodField()

    views = ViewSerializer(many=True, required=False)

    version = core.OnTaskVersionField()

    def get_actions(self, workflow: models.Workflow) -> List[models.Action]:
        """Get the list of selected actions."""
        action_list = self.context.get('selected_actions', [])
        if not action_list:
            # No action needs to be included, no need to call the action
            # serializer
            return []

        # Serialize the content and return data
        serializer = ActionSerializer(
            instance=workflow.actions.filter(id__in=action_list),
            many=True,
            required=False)

        return serializer.data

    @profile
    def create(self, validated_data, **kwargs):
        """Create the new workflow."""
        version = validated_data.pop('version', None)

        wflow_name = self.context.get('name')
        if wflow_name:
            validated_data['name'] = wflow_name
        else:
            wflow_name = validated_data.get('name')
            if not wflow_name:
                raise Exception(_('Unexpected empty workflow name.'))

        if models.Workflow.objects.filter(
            name=wflow_name,
            user=self.context['user']
        ).exists():
            raise Exception(_(
                'There is a workflow with this name. '
                + 'Please provide a workflow name in the import page.'))

        # Insert filter map
        self.context['filter_map'] = {}

        # Get the fields to process later
        columns_data = validated_data.pop('columns', [])
        data_frame_data = validated_data.pop('data_frame')
        views_data = validated_data.pop('views', [])
        actions_data = validated_data.pop('actions', [])

        # Create the workflow
        workflow_obj = None
        try:
            workflow_obj = models.Workflow.objects.create(
                user=self.context['user'],
                **validated_data)
            self.context['workflow'] = workflow_obj

            # Create the columns but don't add them to the df table
            self.context['add_to_df_table'] = False
            columns = [
                ColumnSerializer.create_column(column_data, self.context)
                for column_data in columns_data]

            # If there is any column with position = 0, recompute (this is to
            # guarantee backward compatibility.
            if any(col.position == 0 for col in columns):
                for idx, col in enumerate(columns):
                    col.position = idx + 1
                    col.save()

            # Load the data frame
            if data_frame_data is not None:
                # Store the table in the DB
                pandas.store_table(
                    data_frame_data,
                    workflow_obj.get_data_frame_table_name(),
                    dtype={col.name: col.data_type for col in columns})

            # Create the views pointing to the workflow
            self.context['columns'] = columns
            views = [
                ViewSerializer.create_view(view_data, self.context)
                for view_data in views_data]

            self.context['views'] = views
            for action_data in actions_data:
                ActionSerializer.create_action(action_data, self.context)

        except Exception:
            # Get rid of the objects created
            if workflow_obj:
                if workflow_obj.id:
                    workflow_obj.delete()
            raise

        return workflow_obj

    class Meta:
        """Select model and fields to exclude."""

        model = models.Workflow
        exclude = [
            'user',
            'created',
            'modified',
            'data_frame_table_name',
            'session_key',
            'shared',
            'star',
            'luser_email_column',
            'luser_email_column_md5',
            'lusers',
            'lusers_is_outdated']


class WorkflowImportSerializer(WorkflowExportSerializer):
    """Serializer to make the action field writable.

    This serializer simply overwrites the actions field to make it writeable.
    The rest of the functionality is identical to the WorkflowExportSerializer
    """

    actions = ActionSerializer(many=True, required=False)


class WorkflowLockSerializer(serializers.Serializer):
    """Serializer to transmit the boolean value of the lock in a workflow."""

    lock = serializers.BooleanField()
