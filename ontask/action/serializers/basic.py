# -*- coding: UTF-8 -*-#

"""Classes to serialize Actions."""
from typing import Dict, List

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from ontask import models
from ontask.column.serializers import ColumnNameSerializer, ColumnSerializer
from ontask.condition.serializers import (
    ConditionNameSerializer, ConditionSerializer, FilterSerializer)
from ontask.table.serializers import ViewNameSerializer, ViewSerializer

try:
    profile  # noqa: Z444
except NameError:
    def profile(bogus: int) -> int:
        """Useless, to prevent an emtpy exception handler"""
        return bogus  # noqa E731


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
        fields = ['column', 'condition', 'changes_allowed']


class RubricCellSerializer(serializers.ModelSerializer):
    """Serialize Rubric Cells."""

    column = ColumnNameSerializer(required=True, many=False)

    @staticmethod
    def create_rubric(
        validated_data: Dict,
        context: Dict
    ) -> models.RubricCell:
        """Create the tuple object with column, condition, action.

        :param validated_data: Dictionary with fields
        :param context: Dictionary with context information
        :return: New object
        """
        action = context['action']
        column_data = validated_data.pop('column')
        column = action.workflow.columns.get(name=column_data['name'])

        return models.RubricCell.objects.create(
            action=action,
            column=column,
            **validated_data)

    class Meta:
        """Define the model and select fields to process."""

        model = models.RubricCell
        fields = [
            'column',
            'loa_position',
            'description_text',
            'feedback_text']


class ActionSerializer(serializers.ModelSerializer):
    """Action serializer.

    The serializer does not create any columns and assumes they exist.
    """
    conditions = ConditionSerializer(required=False, many=True)

    # Include the related ActionColumnConditionTuple objects
    column_condition_pair = ColumnConditionNameSerializer(
        many=True,
        required=False)

    # Include the RubricCell objects
    rubric_cells = RubricCellSerializer(many=True, required=False)

    attachments = ViewNameSerializer(required=False, many=True)

    filter = FilterSerializer(required=False, many=False, allow_null=True)

    @staticmethod
    def create_action(validated_data, context: Dict) -> models.Action:
        """Create an action with the validated data and context.

        :param validated_data: Dictionary with the basic data
        :param context: Dictionary with context information
        :return: New action
        """
        workflow = context['workflow']

        # Store the elements that need further processing
        filter_data = validated_data.pop('filter', None)
        conditions_data = validated_data.pop('conditions', [])
        attachments_data = validated_data.pop('attachments', [])
        column_condition_data = validated_data.pop('column_condition_pair', [])
        rubric_cells_data = validated_data.pop('rubric_cells', [])
        # no idea, but this field appears to be added here
        validated_data.pop('user', None)

        # Create the action with the remaining elements
        action_obj = models.Action.objects.create(
            workflow=workflow,
            **validated_data)

        # Update the context to finish up processing
        context['action'] = action_obj

        # Load the attachments in the action
        view_names = [view_data['name'] for view_data in attachments_data]
        action_obj.attachments.set(workflow.views.filter(name__in=view_names))

        # Load the filter pointing to the action
        if filter_data:
            action_obj.filter = FilterSerializer.create_filter(
                filter_data,
                context)
        action_obj.save()

        # Load the conditions pointing to the action
        for condition_data in conditions_data:
            ConditionSerializer.create_condition(condition_data, context)

        # Create the triplets action column condition
        for acc_data in column_condition_data:
            cname = acc_data.pop('column')['name']
            cond_data = acc_data.pop('condition')
            condition = None
            if cond_data:
                condition = action_obj.conditions.filter(
                    name=cond_data['name']).first()
            models.ActionColumnConditionTuple.objects.create(
                action=action_obj,
                column=workflow.columns.filter(name=cname).first(),
                condition=condition,
                **acc_data)

        # Create the rubric data
        for rubric_cell_data in rubric_cells_data:
            RubricCellSerializer.create_rubric(rubric_cell_data, context)

        return action_obj

    @profile
    def create(self, validated_data):
        """Create the action.

        :param validated_data: Validated data
        :return: Create the action in the DB
        """
        action_obj = None
        try:
            action_obj = self.create_action(validated_data, self.context)
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

        exclude = [
            'id',
            'workflow',
            'created',
            'modified',
            'last_executed_log']


class ActionSelfcontainedSerializer(ActionSerializer):
    """Full Action serializer traversing conditions AND columns."""

    used_columns = ColumnSerializer(many=True, required=False)

    used_views = ViewSerializer(many=True, required=False)

    attachments = ViewNameSerializer(many=True, required=False)

    def _process_columns(self, validated_data: List) -> List:
        """Process the used_columns field of a serializer.

        Verifies if the column is new or not. If not new, it verifies that is
        compatible with the columns already existing in the workflow

        :param validated_data: Object with the parsed column items
        :return: List of new columns
        """
        new_columns = []
        for citem in validated_data:
            cname = citem.get('name')
            if not cname:
                raise Exception(
                    _('Incorrect column name {0}.').format(cname))

            # Search for the column in the workflow columns
            col = self.context['workflow'].columns.filter(name=cname).first()
            if not col:
                # Accumulate the new columns just in case we have to undo
                # the changes
                if citem['is_key']:
                    raise Exception(_(
                        'Action contains non-existing key column "{0}"'
                    ).format(cname))
                new_columns.append(citem)
                continue

            # Processing an existing column. Check data type compatibility
            is_not_compatible = (
                col.data_type != citem.get('data_type')
                or col.is_key != citem['is_key']
                or set(col.categories) != set(citem['categories']))
            if is_not_compatible:
                # The two columns are different
                raise Exception(_(
                    'Imported column {0} is different from existing '
                    + 'one.').format(cname))

        return [
            ColumnSerializer.create_column(new_column_info, self.context)
            for new_column_info in new_columns]

    def _process_views(self, validated_data: List) -> List:
        """Process the used_views field of a serializer.

        Verifies that views are all new (no name collisions) and creates
        them.

        :param validated_data: Object with the parsed view items
        :return: List of new views
        """
        workflow = self.context['workflow']
        view_names = [view_data['name'] for view_data in validated_data]
        if workflow.views.filter(name__in=view_names).exists():
            raise Exception(_(
                'The new action creates duplicate view names'))

        return [
            ViewSerializer.create_view(view_data, self.context)
            for view_data in validated_data]

    def create(self, validated_data):
        """Create the Action object with the validated data."""

        workflow = self.context['workflow']

        if not workflow.has_data_frame():
            # Cannot create actions with an empty workflow
            raise Exception(_(
                'Unable to import action '
                + ' in a workflow with and empty data table'))

        name = validated_data['name']
        action_obj = workflow.actions.filter(name=name).first()
        if action_obj:
            # Name collision
            raise Exception(_(
                'Action with name "{0}" already exists'.format(name)))

        # Insert filter map
        self.context['filter_map'] = {}

        new_columns = []
        try:
            new_columns = self._process_columns(
                validated_data.pop('used_columns'))

            new_views = self._process_views(
                 validated_data.pop('used_views', []))

            # Contains attachment/view names, to be processed later
            attachments_data = validated_data.pop('attachments', [])

            # Create the action, conditions and columns/condition-column pairs
            action_obj = super().create(validated_data)

            # Load the attachments in the action
            att_names = [att_data['name'] for att_data in attachments_data]
            action_obj.attachments.set(
                [view for view in new_views if view.name in att_names])

        except Exception:
            if new_columns:
                for col in new_columns:
                    col.delete()
            raise

        return action_obj

    class Meta:
        """Define the model and the field to exclude."""

        model = models.Action
        exclude = [
            'id',
            'workflow',
            'created',
            'modified',
            'last_executed_log']
