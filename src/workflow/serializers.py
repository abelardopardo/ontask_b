# -*- coding: UTF-8 -*-#
from __future__ import unicode_literals, print_function

from rest_framework import serializers
from rest_framework.exceptions import APIException

from action.serializers import ActionSerializer, ActionSerializerDeep
from dataops import ops, pandas_db
from table.serializers import DataFramePandasField
from .models import Workflow, Column


class ColumnSerializer(serializers.ModelSerializer):
    def create(self, validated_data, **kwargs):
        # Create the object, but point to the given workflow
        column_obj = Column(
            name=validated_data['name'],
            workflow=self.context['workflow'],
            data_type=validated_data['data_type'],
            is_key=validated_data['is_key'],
            categories=validated_data['categories']
        )

        column_obj.save()

        return column_obj

    class Meta:
        model = Column
        exclude = ('workflow',)


class WorkflowSerializer(serializers.ModelSerializer):
    def create(self, validated_data, **kwargs):
        attributes = validated_data.get('attributes', {})
        if not isinstance(attributes, dict):
            raise APIException('Attributes must be a dictionary ' +
                               ' of (string, string) pairs.')

        if any([not isinstance(k, basestring) or not isinstance(v, basestring)
                for k, v in attributes.items()]):
            raise APIException('Attributes must be a dictionary (str, str)')

        workflow_obj = Workflow(
            user=self.context['request'].user,
            name=validated_data['name'],
            description_text=validated_data.get('description_text', ''),
            nrows=0,
            ncols=0,
            attributes=attributes
        )

        try:
            workflow_obj.save()
        except Exception:
            raise APIException('Workflow could not be created.')

        return workflow_obj

    class Meta:
        model = Workflow
        fields = ('id', 'name', 'description_text', 'attributes')


class WorkflowExportSerializer(serializers.ModelSerializer):

    # actions = ActionSerializerDeep(many=True, required=False)
    actions = serializers.SerializerMethodField('get_filtered_actions')

    def get_filtered_actions(self, workflow):
        # Get the subset of actions specified in the context
        action_list = self.context.get('selected_actions', None)
        if action_list:
            query_set = workflow.actions.filter()
        else:
            query_set = workflow.actions.all()

        # Serialize the content and return data
        serializer = ActionSerializerDeep(
            instance=query_set,
            many=True,
            required=False)

        return serializer.data

    def create(self, validated_data, **kwargs):
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

        # Create the actions pointing to the workflow
        action_data = ActionSerializer(data=validated_data.get('actions', []),
                                       many=True,
                                       context={'workflow': workflow_obj})

        if action_data.is_valid():
            action_data.save()

        return workflow_obj

    class Meta:
        model = Workflow
        # These fields should not be exported, and they are irrelevant outside
        # of the platform.
        exclude = ('id',
                   'name',
                   'user',
                   'created',
                   'modified',
                   'query_builder_ops',
                   'data_frame_table_name',
                   'nrows',
                   'ncols',
                   'session_key',
                   'shared')


class WorkflowExportCompleteSerializer(WorkflowExportSerializer):

    data_frame = DataFramePandasField(
        required=False,
        help_text='This field must be the Base64 encoded '
                  'result of pandas.to_pickle() function'
    )

    def create(self, validated_data, **kwargs):

        workflow_obj = Workflow(
            user=self.context['user'],
            name=self.context['name'],
            description_text=validated_data['description_text'],
            nrows=validated_data.get('nrows', 0),
            ncols=validated_data.get('ncols', 0),
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

            # Create the actions pointing to the workflow
        action_data = ActionSerializerDeep(
            data=validated_data.get('actions', []),
            many=True,
            context={'workflow': workflow_obj})
        if action_data.is_valid():
            action_data.save()

        # Load the data frame
        data_frame = validated_data.get('data_frame', None)
        if data_frame is not None:
            ops.store_dataframe_in_db(data_frame, workflow_obj.id)
            workflow_obj.data_frame_table_name = \
                pandas_db.create_table_name(workflow_obj.pk)
        workflow_obj.save()

        return workflow_obj

    class Meta:
        model = Workflow
        # These fields should not be exported, and they are irrelevant outside
        # of the platform.
        exclude = ('id',
                   'name',
                   'user',
                   'created',
                   'data_frame_table_name',
                   'modified',
                   'session_key',
                   'shared')

# from workflow.models import Workflow
# from workflow.serializers import WorkflowSerializer, WorkflowSerializerM
# from rest_framework.renderers import JSONRenderer
# from rest_framework.parsers import JSONParser
# from django.utils.six import BytesIO
#
# w1 = Workflow.objects.all()[0]
# w2 = Workflow.objects.all()[1]
# s1 = WorkflowSerializer(w1)
# s2 = WorkflowSerializer(w2)
# s3 = WorkflowSerializer([w1, w2], many=True)

# w1 = WorkflowExportSerializer(Workflow.objects.get(pk=34))
# json = JSONRenderer().render(w1.data)
# stream = BytesIO(json)
# data = JSONParser().parse(stream)
# w2 = WorkflowExportSerializer(data=data)
# w2.is_valid()
# w2.validated_data
