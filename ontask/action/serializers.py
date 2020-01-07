# -*- coding: UTF-8 -*-#

"""Classes to serialize Actions and Conditions."""
from typing import Optional

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from ontask import models
from ontask.column.serializers import (
    ColumnNameSerializer, ColumnSerializer,
)
from ontask.dataops import formula, sql

try:
    profile  # noqa: Z444
except NameError:
    def profile(bogus: int) -> int:
        """Useless, to prevent an emtpy exception handler"""
        return bogus  # noqa E731


def _create_condition(validated_data, action):
    """Create a new condition with the validated data.

    :param validated_data: Dictionary with the data validated by the serializer
    :param action: Action object to use as parent object.
    :return: reference to new condition object.
    """
    condition_obj = models.Condition(
        action=action,
        name=validated_data['name'],
        description_text=validated_data['description_text'],
        formula=validated_data['formula'],
        n_rows_selected=validated_data.get('n_rows_selected', -1),
        is_filter=validated_data['is_filter'],
    )
    condition_obj.save()

    return condition_obj


def _create_columns(new_columns, context):
    """Add new_columns just created to the DB in the given context.

    :param new_columns: List of columns that have been already created
    :param context: Dictionary to pass the serializer with extra info
    :return: List of new column objects
    """
    if not new_columns:
        return []

    workflow = context['workflow']

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
        sql.add_column_to_db(
            workflow.get_data_frame_table_name(),
            col.name,
            col.data_type)

        # Update the column position and count in the workflow
        workflow.ncols = workflow.ncols + 1
        col.position = workflow.ncols
        col.save(update_fields=['position'])

    workflow.save(update_fields=['ncols'])

    return new_columns


def _process_columns(validated_data, context):
    """Process the used_columns field of a serializer.

    Verifies if the column is new or not. If not new, it verifies that is
    compatible with the columns already existing in the workflow

    :param validated_data: Object with the parsed column items
    :param context: dictionary with additional objects for serialization
    :return: List of new columns
    """
    new_columns = []
    for citem in validated_data:
        cname = citem.get('name')
        if not cname:
            raise Exception(
                _('Incorrect column name {0}.').format(cname))

        # Search for the column in the workflow columns
        col = context['workflow'].columns.filter(name=cname).first()
        if not col:
            # Accumulate the new columns just in case we have to undo
            # the changes
            if citem['is_key']:
                raise Exception(
                    _('Action contains non-existing key column "{0}"').format(
                        cname))
            new_columns.append(citem)
            continue

        # Processing an existing column. Check data type compatibility
        is_not_compatible = (
            col.data_type != citem.get('data_type')
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

    return _create_columns(new_columns, context)


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
    def create(self, validated_data, **kwargs) -> Optional[models.Condition]:
        """Create a new condition object based on the validated_data.

        :param validated_data: Validated data obtained by the parser
        :param kwargs: Additional arguments (unused)
        :return: Condition object
        """
        del kwargs
        condition_obj = None
        try:
            condition_obj = _create_condition(
                validated_data,
                self.context['action'])

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
                cnames = formula.get_variables(condition_obj.formula)

            # Set the condition values
            condition_obj.columns.set(
                self.context['action'].workflow.columns.filter(
                    name__in=cnames),
            )

            # If n_rows_selected is -1, reevaluate
            if condition_obj.n_rows_selected == -1:
                condition_obj.update_n_rows_selected()

            # Save condition object
            condition_obj.save()
        except Exception:
            if condition_obj and condition_obj.id:
                condition_obj.delete()
            raise

        return condition_obj

    class Meta:
        """Define object condition and select fields to serialize."""

        model = models.Condition
        exclude = ('id', 'action', 'created', 'modified')


class ConditionNameSerializer(serializers.ModelSerializer):
    """Trivial serializer to dump only the name of the column."""

    class Meta:
        """Select the model and the only field required."""

        model = models.Condition
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
        del kwargs
        action = self.context['action']

        condition_obj = None
        if validated_data.get('condition', {}):
            condition_obj = action.conditions.get(
                name=validated_data['condition']['name'],
            )

        return models.ActionColumnConditionTuple.objects.get_or_create(
            action=action,
            column=action.workflow.columns.get(
                name=validated_data['column']['name']),
            condition=condition_obj,
            changes_allowed=validated_data.get('changes_allowed', False))

    class Meta:
        """Define the model and select only column and condition elements."""

        model = models.ActionColumnConditionTuple
        fields = ('column', 'condition', 'changes_allowed')


class RubricCellSerializer(serializers.ModelSerializer):
    """Serialize Rubric Cells."""

    column = ColumnNameSerializer(required=True, many=False)

    def create(self, validated_data, **kwargs):
        """Create the tuple object with column, condition, action."""
        del kwargs
        action = self.context['action']

        return models.RubricCell.objects.get_or_create(
            action=action,
            column=action.workflow.columns.get(
                name=validated_data['column']['name']),
            loa_position=validated_data['loa_position'],
            description_text=validated_data['description_text'],
            feedback_text=validated_data['feedback_text'])

    class Meta:
        """Define the model and select fields to seralize."""

        model = models.RubricCell
        fields = (
            'column',
            'loa_position',
            'description_text',
            'feedback_text')


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

    # Include the RubricCell objects
    rubric_cells = RubricCellSerializer(many=True, required=False)

    # Needed for backward compatibility
    is_out = serializers.BooleanField(required=False, initial=True)
    content = serializers.CharField(  # noqa Z110
        required=False,
        initial='',
        allow_blank=True)

    @staticmethod
    def create_column_condition_pairs(
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
                    models.ActionColumnConditionTuple(
                        action=action_obj,
                        column=col,
                        condition=None,
                    )
                    for col in wflow_columns if col.name in column_names
                ]
                # Create the objects
                models.ActionColumnConditionTuple.objects.bulk_create(
                    bulk_list)
            else:
                raise Exception(_('Invalid column data'))

        # Parse the column_condition_pair
        column_condition_pairs = ColumnConditionNameSerializer(
            data=validated_data.get('column_condition_pair', []),
            many=True,
            context={'action': action_obj})

        if column_condition_pairs.is_valid():
            column_condition_pairs.save()
        else:
            raise Exception(_('Invalid column condition pair data'))

        # Parse the rubric_cell
        rubric_cells = RubricCellSerializer(
            data=validated_data.get('rubric_cells', []),
            many=True,
            context={'action': action_obj})

        if rubric_cells.is_valid():
            rubric_cells.save()
        else:
            raise Exception(_('Invalid rubric cell data'))

    @profile
    def create(self, validated_data, **kwargs):
        """Create the action.

        :param validated_data: Validated data
        :param kwargs: Extra material (unused)
        :return: Create the action in the DB
        """
        del kwargs
        action_obj = None
        try:
            action_type = validated_data.get('action_type')
            if not action_type:
                if validated_data['is_out']:
                    action_type = models.Action.PERSONALIZED_TEXT
                else:
                    action_type = models.Action.SURVEY

            action_obj = models.Action(
                workflow=self.context['workflow'],
                name=validated_data['name'],
                description_text=validated_data['description_text'],
                action_type=action_type,
                serve_enabled=validated_data['serve_enabled'],
                active_from=validated_data['active_from'],
                active_to=validated_data['active_to'],
                text_content=validated_data.get(
                    'content',
                    validated_data.get('text_content'),  # Legacy
                ),
                target_url=validated_data.get('target_url', ''),
                shuffle=validated_data.get('shuffle', False),
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

            # Process the fields columns (legacy) and column_condition_pairs
            self.create_column_condition_pairs(
                validated_data,
                action_obj,
                self.context['workflow'].columns.all(),
            )
        except Exception:
            if action_obj and action_obj.id:
                models.ActionColumnConditionTuple.objects.filter(
                    action=action_obj,
                ).delete()
                action_obj.delete()
            raise

        return action_obj

    class Meta:
        """Model definition, and exclude fields, instead of include."""

        model = models.Action

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
        if not self.context['workflow'].has_data_frame():
            # Cannot create actions with an empty workflow
            raise Exception(_(
                'Unable to import action '
                + ' in a workflow with and empty data table'))

        new_columns = []
        try:
            new_columns = _process_columns(
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

    class Meta:
        """Define the model and the field to exclude."""

        model = models.Action
        exclude = (
            'id',
            'workflow',
            'created',
            'modified',
            'last_executed_log')
