# -*- coding: UTF-8 -*-#

"""Classes to serialize Actions and Conditions."""

from builtins import object
from typing import Union

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from action.models import Action, ActionColumnConditionTuple, Condition
from dataops.formula_evaluation import get_variables
from dataops.sql_query import add_column
from workflow.column_serializers import ColumnNameSerializer, ColumnSerializer

try:
    profile  # noqa: Z444
except NameError:
    profile = lambda x: x # noqa E731


def create_columns(new_columns, context):
    """Add new_columns just created to the DB in the given context.

    :param new_columns: List of columns that have been already created
    :param context: Dictionary to pass the serializer with extra info
    :return: List of new column objects
    """
    if not new_columns:
        return []

    workflow = context['workflow']
    if not workflow.has_data_frame():
        # Cannot create columns with an empty workflow
        raise Exception(_(
            'Unable to import action '
            + ' in a workflow with and empty data table'))

    # There are some new columns that need to be created
    column_data = ColumnSerializer(
        data=new_columns,
        many=True,
        context=context)

    # And save its content
    if not column_data.is_valid():
        raise Exception(_('Unable to create column data'))
    new_columns = column_data.save()

    # Add columns to DB
    for col in new_columns:
        add_column(
            workflow.get_data_frame_table_name(),
            col.name,
            col.data_type)

        # Update the column position and count in the workflow
        workflow.ncols = workflow.ncols + 1
        col.position = workflow.ncols
        col.save()

    workflow.save()

    return new_columns


def process_columns(validated_data, context):
    """Process the used_columns field of a serializer.

    Verifies if the column is new or not. If not new, it verifies that is
    compatible with the columns already existing in the workflow

    :param validated_data: Object with the parsed column items
    :param context: dictionary with additional objects for serialization
    :return: List of new columns
    """
    new_columns = []
    for citem in validated_data:
        cname = citem.get('name', None)
        if not cname:
            raise Exception(
                _('Incorrect column name {0}.').format(cname))

        # Search for the column in the workflow columns
        col = next(
            (col for col in context['columns'] if col.name == cname),
            None)
        if not col:
            # Accumulate the new columns just in case we have to undo
            # the changes
            new_columns.append(citem)
            continue

        # Processing an existing column. Check data type compatibility
        is_not_compatible = (
            col.data_type != citem.get('data_type', None)
            or col.is_key != citem['is_key']
            or set(col.categories) != set(citem['categories'])
        )
        if is_not_compatible:
            # The two columns are different
            raise Exception(_(
                'Imported column {0} is different from existing '
                + 'one.').format(cname))

        # Update the column categories (just in case the new one has a
        # different order)
        col.set_categories(citem['categories'])

    # Create the new columns if they have been requested
    if not new_columns:
        return new_columns

    return create_columns(new_columns, context)


class ConditionSerializer(serializers.ModelSerializer):
    """Class to serialize a Condition."""

    # The columns field needs a nested serializer because at this point,
    # the column objects must contain only the name (not the entire model).
    # An action is connected to a workflow which has a set of columns
    # attached to it. Thus, the column records are created through the
    # workflow structure, and at this point in the model, only the names are
    # required to restore the many to many relationship.
    columns = ColumnNameSerializer(required=False, many=True)

    @profile
    def create(self, validated_data, **kwargs) -> Union[Condition, None]:
        """Create a new condition object based on the validated_data.

        :param validated_data: Validated data obtained by the parser
        :param kwargs: Additional arguments
        :return: Condition object
        """
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

            # Process columns
            if validated_data.get('columns'):
                # Load the columns pointing to the action (if any)
                columns = ColumnNameSerializer(
                    data=validated_data.get('columns'),
                    many=True,
                    required=False,
                )
                if columns.is_valid():
                    cnames = [cdata['name'] for cdata in columns.data]
                else:
                    raise Exception(_('Incorrect column data'))
            else:
                cnames = get_variables(condition_obj.formula)

            # Set the condition values
            condition_obj.columns.set(
                [col for col in self.context['columns'] if col.name in cnames])

            # Save condition object
            condition_obj.save()
        except Exception:
            if condition_obj and condition_obj.id:
                condition_obj.delete()
            raise

        return condition_obj

    class Meta(object):
        """Define object condition and select fields to serialize."""

        model = Condition
        exclude = ('id', 'action', 'created', 'modified')


class ConditionNameSerializer(serializers.ModelSerializer):
    """Trivial serializer to dump only the name of the column."""

    class Meta(object):
        """Select the model and the only field required."""

        model = Condition
        fields = ('name',)


class ColumnConditionNameSerializer(serializers.ModelSerializer):
    """Serialize Column/ConditionName tuples."""

    column = ColumnNameSerializer(required=True, many=False)

    condition = ConditionNameSerializer(
        required=False,
        allow_null=True,
        many=False)

    def create(self, validated_data, **kwargs):
        """Create the tuple object with column, condition, action."""
        action = self.context['action']
        columns = self.context['columns']

        condition_obj = None
        if validated_data.get('condition', {}):
            condition_obj = action.conditions.get(
                name=validated_data['condition']['name'],
            )
        return ActionColumnConditionTuple.objects.get_or_create(
            action=action,
            column=next(
                col for col in columns
                if col.name == validated_data['column']['name']),
            condition=condition_obj)

    class Meta(object):
        """Define the model and select only column and condition elements."""

        model = ActionColumnConditionTuple
        fields = ('column', 'condition')


class ActionSerializer(serializers.ModelSerializer):
    """Action serializer recursively traversing conditions but not columns.

    The serializer does not create any columns and relies on them being
    already created and receiving only the names
    """

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
    column_condition_pair = ColumnConditionNameSerializer(
        many=True,
        required=False)
    # Needed for backward compatibility
    is_out = serializers.BooleanField(required=False, initial=True)

    def create_column_condition_pairs(
        self,
        validated_data,
        action_obj,
        wflow_columns,
    ):
        """Create the column_condition pairs.

        :param validated_data: Source data
        :param action_obj: action hosting the condition
        :param wflow_columns: All the columns available
        :return: Create the objects and store them in the DB
        """
        field_data = validated_data.get('columns', [])
        if field_data:
            # Load the columns pointing to the action (if any) LEGACY FIELD!!
            columns = ColumnNameSerializer(
                data=field_data,
                many=True,
                required=False)

            if columns.is_valid():
                # Legacy field "columns". Iterate over the names and create
                # the triplets.
                # First get the column names returned by the serailizer
                column_names = [col_data['name'] for col_data in columns.data]
                # List for bulk creation of objects
                bulk_list = [
                    ActionColumnConditionTuple(
                        action=action_obj,
                        column=col,
                        condition=None,
                    )
                    for col in wflow_columns if col.name in column_names
                ]
                # Create the objects
                ActionColumnConditionTuple.objects.bulk_create(bulk_list)
            else:
                raise Exception(_('Invalid column data'))

        field_data = validated_data.get('column_condition_pair', [])
        if field_data:
            # Parse the column_condition_pair
            column_condition_pairs = ColumnConditionNameSerializer(
                data=field_data,
                many=True,
                context={
                    'action': action_obj,
                    'columns': wflow_columns})

            if column_condition_pairs.is_valid():
                column_condition_pairs.save()
            else:
                raise Exception(_('Invalid column condition pair data'))

    @profile
    def create(self, validated_data, **kwargs):
        """Create the action.

        :param validated_data: Validated data
        :param kwargs: Extra material
        :return: Create the action in the DB
        """
        action_obj = None
        try:
            action_type = validated_data.get('action_type', None)
            if not action_type:
                if validated_data['is_out']:
                    action_type = Action.personalized_text
                else:
                    action_type = Action.survey

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
                shuffle=validated_data.get('shuffle', default=False),
            )
            action_obj.save()

            # Load the conditions pointing to the action
            condition_data = ConditionSerializer(
                data=validated_data.get('conditions', []),
                many=True,
                context={
                    'action': action_obj,
                    'columns': self.context['columns']})
            if condition_data.is_valid():
                condition_data.save()
            else:
                raise Exception(_('Invalid condition data'))

            # Process the fields columns (legacy) and column_condition_pairs
            self.create_column_condition_pairs(
                validated_data,
                action_obj,
                self.context['columns'],
            )
        except Exception:
            if action_obj and action_obj.id:
                ActionColumnConditionTuple.objects.filter(
                    action=action_obj,
                ).delete()
                action_obj.delete()
            raise

        return action_obj

    class Meta(object):
        """Model definition, and exclude fields, instead of include."""

        model = Action

        exclude = (
            'id',
            'workflow',
            'created',
            'modified',
            'last_executed_log')


class ActionSelfcontainedSerializer(ActionSerializer):
    """Full Action serializer traversing conditions AND columns."""

    used_columns = ColumnSerializer(many=True, required=False)

    def create(self, validated_data, **kwargs):
        """Create the Action object with the validated data."""
        new_columns = []
        try:
            new_columns = process_columns(
                validated_data['used_columns'],
                self.context)

            # Create the action, conditions and columns/condition-column pairs
            action_obj = super().create(validated_data, **kwargs)
        except Exception:
            if new_columns:
                for col in new_columns:
                    col.delete()
            raise

        return action_obj

    class Meta(object):
        """Define the model and the field to exclude."""

        model = Action

        exclude = (
            'id',
            'workflow',
            'created',
            'modified',
            'last_executed_log')
