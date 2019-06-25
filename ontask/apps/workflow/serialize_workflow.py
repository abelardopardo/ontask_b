# -*- coding: UTF-8 -*-#

"""Serializers to import/export, list the workflows."""

from builtins import object, str

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import APIException

from action.serializers import ActionSerializer
from dataops.pandas import store_table
from table.serializers import DataFramePandasField, ViewSerializer
from workflow.models import Workflow
from workflow.serialize_column import ColumnSerializer

try:
    profile  # noqa: Z444
except NameError:
    def profile(bogus): return bogus  # noqa: E731


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
            workflow_obj = Workflow(
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

    class Meta(object):
        """Select model and fields to consider."""

        model = Workflow

        fields = ('id', 'name', 'description_text', 'attributes')


class WorkflowExportSerializer(serializers.ModelSerializer):
    """Serializer to export the workflow.

    This serializer is use to export Workflows selecting a subset of actions.
    Since the SerializerMethodField used for the selection is a read_only
    field, the import is managed by a different serializer that uses a
    regular one for the action field (see WorkflowImportSerializer)
    """

    actions = serializers.SerializerMethodField()

    data_frame = DataFramePandasField(
        required=False,
        allow_null=True,
        help_text=_(
            'This field must be the Base64 encoded '
            + 'result of pandas.to_pickle() function'),
    )

    columns = ColumnSerializer(many=True, required=False)

    views = ViewSerializer(many=True, required=False)

    version = serializers.CharField(
        read_only=True,
        default='NO VERSION',
        allow_blank=True,
        label='OnTask Version',
        help_text=_('To guarantee compability'))

    def get_actions(self, workflow):
        """Get the list of selected actions."""
        action_list = self.context.get('selected_actions', [])
        if not action_list:
            # No action needs to be included, no need to call the action
            # serializer
            return []

        # Execute the query set
        query_set = workflow.actions.filter(id__in=action_list)

        # Serialize the content and return data
        serializer = ActionSerializer(
            instance=query_set,
            many=True,
            required=False)

        return serializer.data

    @profile
    def create(self, validated_data, **kwargs):
        """Create the new workflow."""
        wflow_name = self.context.get('name')
        if not wflow_name:
            wflow_name = self.validated_data.get('name')
            if not wflow_name:
                raise Exception(_('Unexpected empty workflow name.'))

            if Workflow.objects.filter(
                name=wflow_name,
                user=self.context['user']
            ).exists():
                raise Exception(_(
                    'There is a workflow with this name. '
                    + 'Please provide a workflow name in the import page.'))

        # Initial values
        workflow_obj = None
        try:
            workflow_obj = Workflow(
                user=self.context['user'],
                name=wflow_name,
                description_text=validated_data['description_text'],
                nrows=0,
                ncols=0,
                attributes=validated_data['attributes'],
                query_builder_ops=validated_data.get('query_builder_ops', {}),
            )
            workflow_obj.save()

            # Create the columns
            column_data = ColumnSerializer(
                data=validated_data.get('columns', []),
                many=True,
                context={'workflow': workflow_obj})
            # And save its content
            if column_data.is_valid():
                columns = column_data.save()
            else:
                raise Exception(_('Unable to save column information'))

            # If there is any column with position = 0, recompute (this is to
            # guarantee backward compatibility.
            if any(col.position == 0 for col in columns):
                for idx, col in enumerate(columns):
                    col.position = idx + 1
                    col.save()

            # Load the data frame
            data_frame = validated_data.get('data_frame')
            if data_frame is not None:
                # Store the table in the DB
                store_table(
                    data_frame,
                    workflow_obj.get_data_frame_table_name(),
                    dtype={
                        col.name: col.data_type
                        for col in workflow_obj.columns.all()
                    },
                )

                # Reconcile now the information in workflow and columns with
                # the one loaded
                workflow_obj.ncols = validated_data['ncols']
                workflow_obj.nrows = validated_data['nrows']

                workflow_obj.save()

            # Create the actions pointing to the workflow
            action_data = ActionSerializer(
                data=validated_data.get('actions', []),
                many=True,
                context={'workflow': workflow_obj, 'columns': columns})

            if action_data.is_valid():
                action_data.save()
            else:
                raise Exception(_('Unable to save column information'))

            # Create the views pointing to the workflow
            view_data = ViewSerializer(
                data=validated_data.get('views', []),
                many=True,
                context={'workflow': workflow_obj, 'columns': columns})

            if view_data.is_valid():
                view_data.save()
            else:
                raise Exception(_('Unable to save column information'))
        except Exception:
            # Get rid of the objects created
            if workflow_obj:
                if workflow_obj.id:
                    workflow_obj.delete()
            raise

        return workflow_obj

    class Meta(object):
        """Select model and fields to exclude."""

        model = Workflow

        exclude = (
            'id',
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
            'lusers_is_outdated',
        )


class WorkflowImportSerializer(WorkflowExportSerializer):
    """Serializer to make the action field writable.

    This serializer simply overwrites the actions field to make it writeable.
    The rest of the functionality is identical to the WorkflowExportSerializer
    """

    actions = ActionSerializer(many=True, required=False)


class WorkflowLockSerializer(serializers.Serializer):
    """Serializer to transmit the boolean value of the lock in a workflow."""

    lock = serializers.BooleanField()
