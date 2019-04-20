# -*- coding: UTF-8 -*-#


from builtins import object

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from dataops import pandas_db, ops
from dataops.formula_evaluation import get_variables
from workflow.column_serializers import ColumnSerializer, ColumnNameSerializer
from .models import Condition, Action, ActionColumnConditionTuple


try:
    profile
except NameError:
    profile = lambda x: x


class ConditionSerializer(serializers.ModelSerializer):
    # The columns field needs a nested serializer because at this point,
    # the column objects must contain only the name (not the entire model).
    # An action is connected to a workflow which has a set of columns
    # attached to it. Thus, the column records are created through the
    # workflow structure, and at this point in the model, only the names are
    # required to restore the many to many relationship.
    columns = ColumnNameSerializer(required=False, many=True)

    @profile
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
                [x for x in self.context['columns'] if x.name in cnames]
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

    class Meta(object):
        model = Condition
        exclude = ('id', 'action', 'created', 'modified')


class ConditionNameSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Condition
        fields = ('name',)


class ColumnConditionNameSerializer(serializers.ModelSerializer):
    column = ColumnNameSerializer(required=True, many=False)

    condition = ConditionNameSerializer(required=False,
                                        allow_null=True,
                                        many=False)

    def create(self, validated_data, **kwargs):
        action = self.context['action']
        columns = self.context['columns']

        condition_obj = None
        if validated_data.get('condition', {}):
            condition_obj = action.conditions.get(
                name=validated_data['condition']['name']
            )
        objt = ActionColumnConditionTuple.objects.get_or_create(
            action=action,
            column=next(x for x in columns
                        if x.name == validated_data['column']['name']),
            condition=condition_obj
        )
        return obj

    class Meta(object):
        model = ActionColumnConditionTuple
        fields = ('column', 'condition')


class ActionSerializer(serializers.ModelSerializer):
    conditions = ConditionSerializer(required=False, many=True)

    # The columns field is a legacy construct. It needs a nested serializer
    # because at this point,
    # the column objects must contain only the name (not the entire model).
    # An action is connected to a workflow which has a set of columns
    # attached to it. Thus, the column records are created through the
    # workflow structure, and at this point in the model, only the names are
    # required to then restore the many to many relationship.
    columns = ColumnNameSerializer(required=False, many=True)

    # Include the related ActionColumnConditionTuple objects
    column_condition_pair = ColumnConditionNameSerializer(many=True,
                                                          required=False)
    # Needed for backward compatibility
    is_out = serializers.BooleanField(required=False, initial=True)

    def create_column_condition_pairs(self,
                                      validated_data,
                                      action_obj,
                                      wflow_columns):
        # Load the columns pointing to the action (if any) LEGACY FIELD!!
        columns = ColumnNameSerializer(
            data=validated_data.get('columns', []),
            many=True,
            required=False,
        )
        if columns.is_valid():
            # Legacy field "columns". Iterate over the names and create
            # the triplets.
            # First get the column names returned by the seralizer
            column_names = [x['name'] for x in columns.data]
            # List for bulk creation of objects
            bulk_list = [
                ActionColumnConditionTuple.objects.get_or_create(
                    action=action_obj,
                    column=x,
                    condition=None
                )
                for x in wflow_columns if x.name in column_names]
            # Create the objects
            ActionColumnConditionTuple.objects.bulk_create(bulk_list)
        else:
            raise Exception(_('Invalid column data'))

        # Parse the column_condition_pair
        column_condition_pairs = ColumnConditionNameSerializer(
            data=validated_data.get('column_condition_pair', []),
            many=True,
            context={'action': action_obj,
                     'columns': wflow_columns}
        )

        if column_condition_pairs.is_valid():
            column_condition_pairs.save()
        else:
            raise Exception(_('Invalid column condition pair data'))

    @profile
    def create(self, validated_data, **kwargs):
        action_obj = None
        try:
            action_type = validated_data.get('action_type', None)
            if not action_type:
                if validated_data['is_out']:
                    action_type = Action.PERSONALIZED_TEXT
                else:
                    action_type = Action.SURVEY

            action_obj = Action(
                workflow=self.context['workflow'],
                name=validated_data['name'],
                description_text=validated_data['description_text'],
                action_type=action_type,
                serve_enabled=validated_data['serve_enabled'],
                active_from=validated_data['active_from'],
                active_to=validated_data['active_to'],
                content=validated_data.get('content', None),
                target_url=validated_data.get('target_url', None),
                shuffle=validated_data.get('shuffle', False)
            )

            action_obj.save()

            # Load the conditions pointing to the action
            condition_data = ConditionSerializer(
                data=validated_data.get('conditions', []),
                many=True,
                context={'action': action_obj,
                         'columns': self.context['columns']})
            if condition_data.is_valid():
                condition_data.save()
            else:
                raise Exception(_('Invalid condition data'))

            # Process the fields columns (legacy) and column_condition_pairs
            self.create_column_condition_pairs(
                validated_data,
                action_obj,
                self.context['columns']
            )
        except Exception:
            if action_obj and action_obj.id:
                ActionColumnConditionTuple.objects.filter(
                    action=action_obj
                ).delete()
                action_obj.delete()
            raise

        return action_obj

    # To get both Actions and Conditions
    class Meta(object):
        model = Action

        exclude = ('id',
                   'workflow',
                   'created',
                   'modified',
                   'last_executed_log')


class ActionSelfcontainedSerializer(ActionSerializer):
    used_columns = ColumnSerializer(many=True, required=False)

    def create(self, validated_data, **kwargs):
        wflow_columns = self.context['columns']
        new_columns = []
        try:
            # Process first the used_columns field to get a sense of how many
            # columns, their type how many of them new, etc. etc.
            for citem in validated_data['used_columns']:
                cname = citem.get('name', None)
                if not cname:
                    raise Exception(
                        _('Incorrect column name {0}.').format(cname))

                # Search for the column in the workflow columns
                col = next((x for x in wflow_columns if x.name == cname), None)
                if not col:
                    # Accumulate the new columns just in case we have to undo
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

                # Update the column categories (just in case the new one has a
                # different order)
                col.set_categories(citem['categories'])

            # Remember the column names to remove them if needed
            new_column_names = [x['name'] for x in new_columns]

            # Create the new columns if they have been requested
            if new_columns:
                # There are some new columns that need to be created
                column_data = ColumnSerializer(data=new_columns,
                                               many=True,
                                               context=self.context)

                # And save its content
                if column_data.is_valid():
                    new_columns = column_data.save()
                    workflow = self.context['workflow']
                    df = pandas_db.load_from_db(
                        workflow.get_data_frame_table_name())
                    if df is None:
                        raise Exception(
                            _('Action cannot be imported with and '
                              'empty data table')
                        )

                    for col in new_columns:
                        # Add the column with the initial value
                        df = ops.data_frame_add_column(df, col, None)

                        # Update the column position
                        col.position = len(df.columns)
                        col.save()

                    # Store the df to DB
                    ops.store_dataframe(df, workflow)
                else:
                    raise Exception(_('Unable to create column data'))

            # Create the action, conditions and columns/condition-column pairs
            action_obj = super().create(validated_data, **kwargs)

        except Exception:
            if new_columns:
                [x.delete() for x in new_columns]
            raise

        return action_obj

    class Meta(object):
        model = Action

        exclude = ('id',
                   'workflow',
                   'created',
                   'modified',
                   'last_executed_log')
