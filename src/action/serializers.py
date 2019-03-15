# -*- coding: UTF-8 -*-#


from builtins import object
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from dataops import pandas_db, ops
from dataops.formula_evaluation import get_variables
from workflow.column_serializers import ColumnSerializer
from workflow.models import Column
from .models import Condition, Action, ActionColumnConditionTuple


class ColumnNameSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Column
        fields = ('name',)


class ConditionSerializer(serializers.ModelSerializer):
    # The columns field needs a nested serializer because at this point,
    # the column objects must contain only the name (not the entire model).
    # An action is connected to a workflow which has a set of columns
    # attached to it. Thus, the column records are created through the
    # workflow structure, and at this point in the model, only the names are
    # required to restore the many to many relationship.
    columns = ColumnNameSerializer(required=False, many=True)

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
                condition_obj.action.workflow.columns.filter(name__in=cnames)
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

    condition = ConditionNameSerializer(required=False, many=False)

    def create(self, validated_data, **kwargs):
        action = self.context['action']
        tuples = []
        if validated_data.get('columns'):
            #
            # Load the columns pointing to the action (if any)
            # This is here for backward compatibility
            #
            columns = ColumnNameSerializer(
                data=validated_data.get('columns'),
                many=True,
                required=False
            )
            if columns.is_valid():
                tuples = []
                for citem in columns.data:
                    tuples.append(
                        {'column': {'name': citem['name']},
                         'condition': None}
                    )
            else:
                raise Exception(_('Invalid column data'))
        else:
            #
            # Load the column_condition_tuples if they exist
            #
            column_condition_tuple_data = validated_data.get(
                'column_condition_tuples'
            )
            if column_condition_tuple_data:
                tuples = ColumnConditionNameSerializer(
                    data=column_condition_tuple_data,
                    many=True,
                    required=False
                )
            if not tuples.is_valid():
                raise Exception(_('Invalid column data'))

        for item in tuples:
            condition_obj = None
            if item['condition']:
                condition_obj = action.conditions.get(
                    name=item['condition']['name']
                )
            __, __ = \
                ActionColumnConditionTuple.objects.get_or_create(
                    action=action,
                    column=action.wokflow.columns.get(
                        name=item['column']['name']
                    ),
                    condition=condition_obj
                )

    class Meta(object):
        model = ActionColumnConditionTuple
        fields = ('column', 'condition')


class ActionSerializer(serializers.ModelSerializer):
    conditions = ConditionSerializer(required=False, many=True)

    # Include the related ActionColumnConditionTuple objects
    column_condition_tuples = serializers.SerializerMethodField(
        'get_column_condition_tuples'
    )

    # Needed for backward compatibility
    is_out = serializers.BooleanField(required=False, initial=True)

    def get_column_condition_tuples(self, action):
        """
        Method to filter the relevant column, condition pairs and serialize its
        content.
        :param action: Action object being considered
        :return: Serialized data
        """

        # Get the query
        query_set = ActionColumnConditionTuple.filter(action=action)

        # Serialize the objects
        serializer = ColumnConditionNameSerializer(
            instance=query_set,
            many=True,
            required=True
        )

        return serializer.data

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
                context={'action': action_obj})
            if condition_data.is_valid():
                condition_data.save()
            else:
                raise Exception(_('Invalid condition data'))

            # Load the column/condition data
            if validated_data.get('column_condition_tuples'):
                __ = ColumnConditionNameSerializer(
                    data=validated_data.get('column_condition_tuples'),
                    many=True,
                    context={'action': action_obj}
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


class ActionSelfcontainedSerializer(serializers.ModelSerializer):
    conditions = ConditionSerializer(required=False, many=True)

    used_columns = ColumnSerializer(many=True, required=False)

    column_condition_tuples = serializers.SerializerMethodField()

    def get_column_condition_tuples(self, action):
        """
        Method to filter the relevant column, condition pairs and serialize its
        content.
        :param action: Action object being considered
        :return: Serialized data
        """

        # Get the query
        query_set = ActionColumnConditionTuple.objects.filter(action=action)

        # Serialize the objects
        serializer = ColumnConditionNameSerializer(
            instance=query_set,
            many=True,
            required=True
        )

        return serializer.data

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
                # if citem['is_key']:
                #     raise Exception(
                #         _('New action cannot have non-existing key '
                #           'column {0}').format(cname))

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

        new_column_names = [x['name'] for x in new_columns]

        action_type = validated_data.get('action_type', None)
        if not action_type:
            if validated_data.get('is_out'):
                action_type = Action.PERSONALIZED_TEXT
            else:
                action_type = Action.SURVEY

        action_obj = None
        try:
            # used_columns has been verified.
            action_obj = Action(
                workflow=self.context['workflow'],
                name=validated_data['name'],
                description_text=validated_data['description_text'],
                action_type=action_type,
                serve_enabled=validated_data['serve_enabled'],
                active_from=validated_data['active_from'],
                active_to=validated_data['active_to'],
                content=validated_data.get('content', ''),
                target_url=validated_data.get('target_url', None),
                shuffle=validated_data.get('shuffle', False)
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
                        self.context['workflow'].columns.filter(
                            name__in=col_names)
                    )

            # Load the column/condition data, if it exists
            if validated_data.get('column_condition_tuples'):
                __ = ColumnConditionNameSerializer(
                    data=validated_data.get('column_condition_tuples'),
                    many=True,
                    context={'action': action_obj}
                )
        except Exception:
            if action_obj and action_obj.id:
                ActionColumnConditionTuple.objects.filter(
                    action=action_obj
                ).delete()
                action_obj.delete()
            Column.objects.filter(
                workflow=self.context['workflow'],
                name__in=new_column_names).delete()
            raise

        return action_obj

    class Meta(object):
        model = Action

        exclude = ('id',
                   'workflow',
                   'created',
                   'modified',
                   'last_executed_log')
