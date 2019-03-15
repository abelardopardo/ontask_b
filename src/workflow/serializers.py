# -*- coding: UTF-8 -*-#


from builtins import object
from builtins import str
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import APIException

from action.serializers import ActionSerializer
from dataops import ops, pandas_db
from table.serializers import DataFramePandasField, ViewSerializer
from workflow.column_serializers import ColumnSerializer
from .models import Workflow


class WorkflowListSerializer(serializers.ModelSerializer):

    def create(self, validated_data, **kwargs):
        attributes = validated_data.get('attributes', {})
        if not isinstance(attributes, dict):
            raise APIException(
                _('Attributes must be a dictionary of (string, string) pairs.')
            )

        if any([not isinstance(k, str) or not isinstance(v, str)
                for k, v in list(attributes.items())]):
            raise APIException(_('Attributes must be a dictionary (str, str)'))

        workflow_obj = None
        try:
            workflow_obj = Workflow(
                user=self.context['request'].user,
                name=validated_data['name'],
                description_text=validated_data.get('description_text', ''),
                nrows=0,
                ncols=0,
                attributes=attributes
            )

            workflow_obj.save()
        except Exception:
            if workflow_obj and workflow_obj.id:
                workflow_obj.delete()
            raise APIException(_('Workflow could not be created.'))

        return workflow_obj

    class Meta(object):
        model = Workflow
        fields = ('id', 'name', 'description_text', 'attributes')


class WorkflowExportSerializer(serializers.ModelSerializer):
    """
    This serializer is use to export Workflows selecting a subset of
    actions. Since the SerializerMethodField used for the selection is a
    read_only field, the import is managed by a different serializer that
    uses a regular one for the action field (see WorkflowImportSerializer)
    """

    actions = serializers.SerializerMethodField()

    data_frame = DataFramePandasField(
        required=False,
        help_text=_('This field must be the Base64 encoded '
                    'result of pandas.to_pickle() function')
    )

    columns = ColumnSerializer(many=True, required=False)

    views = ViewSerializer(many=True, required=False)

    version = serializers.CharField(read_only=True,
                                    default='NO VERSION',
                                    allow_blank=True,
                                    label="OnTask Version",
                                    help_text=_("To guarantee compability"))

    def get_actions(self, workflow):
        # Get the subset of actions specified in the context
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

    def create(self, validated_data, **kwargs):

        # Initial values
        workflow_obj = None
        try:
            workflow_obj = Workflow(
                user=self.context['user'],
                name=self.context['name'],
                description_text=validated_data['description_text'],
                nrows=0,
                ncols=0,
                attributes=validated_data['attributes'],
                query_builder_ops=validated_data.get('query_builder_ops', {})
            )
            workflow_obj.save()

            # Create the columns
            column_data = ColumnSerializer(
                data=validated_data.get('columns', []),
                many=True,
                context={'workflow': workflow_obj})
            # And save its content
            if column_data.is_valid():
                column_data.save()
            else:
                raise Exception(_('Unable to save column information'))

            # If there is any column with position = 0, recompute (this is to
            # guarantee backward compatibility.
            if workflow_obj.columns.filter(position=0).exists():
                for idx, c in enumerate(workflow_obj.columns.all()):
                    c.position = idx + 1
                    c.save()

            # Load the data frame
            data_frame = validated_data.get('data_frame', None)
            if data_frame is not None:
                ops.store_dataframe_in_db(data_frame,
                                          workflow_obj.id,
                                          reset_keys=False)

                # Reconcile now the information in workflow and columns with the
                # one loaded
                workflow_obj.data_frame_table_name = \
                    pandas_db.create_table_name(workflow_obj.pk)

                workflow_obj.ncols = validated_data['ncols']
                workflow_obj.nrows = validated_data['nrows']

                workflow_obj.save()

            # Create the actions pointing to the workflow
            action_data = ActionSerializer(
                data=validated_data.get('actions', []),
                many=True,
                context={'workflow': workflow_obj}
            )
            if action_data.is_valid():
                action_data.save()
            else:
                raise Exception(_('Unable to save column information'))

            # Create the views pointing to the workflow
            view_data = ViewSerializer(
                data=validated_data.get('views', []),
                many=True,
                context={'workflow': workflow_obj}
            )
            if view_data.is_valid():
                view_data.save()
            else:
                raise Exception(_('Unable to save column information'))
        except Exception:
            # Get rid of the objects created
            if workflow_obj:
                if workflow_obj.has_data_frame():
                    pandas_db.delete_table(workflow_obj.id)
                if workflow_obj.id:
                    workflow_obj.delete()
            raise

        return workflow_obj

    class Meta(object):
        model = Workflow
        # fields = ('description_text', 'nrows', 'ncols', 'attributes',
        #           'query_builder_ops', 'columns', 'data_frame', 'actions')

        exclude = ('id', 'user', 'created', 'modified', 'data_frame_table_name',
                   'session_key', 'shared')


class WorkflowImportSerializer(WorkflowExportSerializer):
    """
    This serializer simply overwrites the actions field to make it writeable.
    The rest of the functionality is identical to the WorkflowExportSerializer
    """

    actions = ActionSerializer(many=True, required=False)


class WorkflowLockSerializer(serializers.Serializer):
    """
    Serializer to transmit the boolean value of the lock in a workflow
    """

    lock = serializers.BooleanField()


