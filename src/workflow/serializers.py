# -*- coding: UTF-8 -*-#
from __future__ import unicode_literals, print_function

from builtins import str
from rest_framework import serializers
from rest_framework.exceptions import APIException
from django.utils.translation import ugettext_lazy as _

from action.models import Action
from action.serializers import ActionSerializer, ConditionSerializer, \
    ColumnNameSerializer
from dataops import ops, pandas_db
from dataops.formula_evaluation import get_variables
from dataops.pandas_db import pandas_datatype_names
from table.serializers import DataFramePandasField, ViewSerializer
from .models import Workflow, Column


class ColumnSerializer(serializers.ModelSerializer):

    def create(self, validated_data, **kwargs):

        # Preliminary checks
        data_type = validated_data.get('data_type', None)
        if data_type is None or \
                data_type not in pandas_datatype_names.values():
            # The data type is not legal
            raise Exception(_('Incorrect data type {0}.').format(data_type))

        column_obj = None
        try:
            # Create the object, but point to the given workflow
            column_obj = Column(
                name=validated_data['name'],
                description_text=validated_data.get('description_text', ''),
                workflow=self.context['workflow'],
                data_type=data_type,
                is_key=validated_data.get('is_key', False),
                position=validated_data.get('position', 0),
                in_viz=validated_data.get('in_viz', True),
                active_from=validated_data.get('active_from', None),
                active_to=validated_data.get('active_to', None),
            )

            # Set the categories if they exists
            column_obj.set_categories(validated_data.get('categories', []), True)

            if column_obj.active_from and column_obj.active_to and \
                    column_obj.active_from > column_obj.active_to:
                raise Exception(
                    _('Incorrect date/times in the active window for '
                      'column {0}').format(validated_data['name']))

            # All tests passed, proceed to save the object.
            column_obj.save()
        except Exception as e:
            if column_obj:
                column_obj.delete()
            raise e

        return column_obj

    class Meta:
        model = Column
        exclude = ('id', 'workflow')


class WorkflowListSerializer(serializers.ModelSerializer):

    def create(self, validated_data, **kwargs):
        attributes = validated_data.get('attributes', {})
        if not isinstance(attributes, dict):
            raise APIException(
                _('Attributes must be a dictionary of (string, string) pairs.')
            )

        if any([not isinstance(k, str) or not isinstance(v, str)
                for k, v in attributes.items()]):
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

    class Meta:
        model = Workflow
        fields = ('id', 'name', 'description_text', 'attributes')


class WorkflowExportSerializer(serializers.ModelSerializer):
    """
    This serializer is use to export Workflows selecting a subset of
    actions. Since the SerializerMethodField used for the selection is a
    read_only field, the import is managed by a different serializer that
    uses a regular one for the action field (see WorkflowImportSerializer)
    """

    actions = serializers.SerializerMethodField('get_filtered_actions')

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

    def get_filtered_actions(self, workflow):
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
                ops.store_dataframe_in_db(data_frame, workflow_obj.id)

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

    class Meta:
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


class ActionSelfcontainedSerializer(serializers.ModelSerializer):
    conditions = ConditionSerializer(required=False, many=True)

    used_columns = ColumnSerializer(many=True, required=False)

    columns = ColumnNameSerializer(required=False, many=True)

    def create(self, validated_data, **kwargs):

        # Process first the used_columns field to get a sense of how many
        # columns, their type how many of them new, etc. etc.
        new_columns = []
        for citem in validated_data['used_columns']:
            cname = citem.get('name', None)
            if not cname:
                raise Exception(_('Incorrect column name {0}.').format(cname))
            col = Column.objects.filter(workflow=self.context['workflow'],
                                        name=cname).first()
            if not col:
                # new column
                if citem['is_key']:
                    raise Exception(
                        _('New action cannot have non-existing key '
                          'column {0}').format(cname))

                # Accummulate the new columns just in case we have to undo
                # the changes
                new_columns.append(citem)
                continue

            # existing column
            if col.data_type != citem.get('data_type', None) or \
                    col.is_key != citem['is_key'] or \
                    set(col.categories) != set(citem['categories']):
                # The two columns are different
                raise Exception(
                    _('Imported column {0} is different from existing '
                      'one.').format(cname)
                )
        new_column_names = [x['name'] for x in new_columns]

        action_obj = None
        try:
            # used_columns has been verified.
            action_obj = Action(
                workflow=self.context['workflow'],
                name=validated_data['name'],
                description_text=validated_data['description_text'],
                is_out=validated_data['is_out'],
                serve_enabled=validated_data['serve_enabled'],
                active_from=validated_data['active_from'],
                active_to=validated_data['active_to'],
                content=validated_data.get('content', '')
            )

            action_obj.save()

            if new_columns:
                # There are some new columns that need to be created
                column_data = ColumnSerializer(data=new_columns,
                                               many=True,
                                               context=self.context)

                # And save its content
                if column_data.is_valid():
                    column_data.save()
                    workflow = self.context['workflow']
                    df = pandas_db.load_from_db(self.context['workflow'].id)
                    if df is None:
                        # If there is no data frame, there is no point on
                        # adding columns.
                        Column.objects.filter(
                            workflow=self.context['workflow'],
                            name__in=new_column_names).delete()
                        action_obj.delete()
                        raise Exception(
                            _('Action cannot be imported with and '
                              'empty data table')
                        )

                    for col in Column.objects.filter(
                            workflow=workflow,
                            name__in=new_column_names):
                        # Add the column with the initial value
                        df = ops.data_frame_add_column(df, col, None)

                        # Update the column position
                        col.position = len(df.columns)
                        col.save()

                    # Store the df to DB
                    ops.store_dataframe_in_db(df, workflow.id)
                else:
                    raise Exception(_('Unable to create column data'))

            # Load the conditions pointing to the action
            condition_data = ConditionSerializer(
                data=validated_data.get('conditions', []),
                many=True,
                context={'action': action_obj})
            if condition_data.is_valid():
                condition_data.save()
            else:
                raise Exception(_('Unable to create condition information'))

            # Update the condition variables for each formula if not present
            for condition in action_obj.conditions.all():
                if condition.columns.all().count() == 0:
                    col_names = get_variables(condition.formula)
                    # Add the corresponding columns to the condition
                    condition.columns.set(
                        self.context['workflow'].columns.filter(name__in=col_names)
                    )

            # Load the columns field
            columns = ColumnNameSerializer(
                data=validated_data['columns'],
                many=True,
                required=False,
                context=self.context
            )
            if columns.is_valid():
                for citem in columns.data:
                    column = action_obj.workflow.columns.get(name=citem['name'])
                    action_obj.columns.add(column)
                columns.save()
            else:
                raise Exception(_('Unable to create columns field'))
        except Exception:
            if action_obj and action_obj.id:
                action_obj.delete()
            Column.objects.filter(
                workflow=self.context['workflow'],
                name__in=new_column_names).delete()
            raise

        return action_obj

    class Meta:
        model = Action

        exclude = ('id',
                   'workflow',
                   'created',
                   'modified')
