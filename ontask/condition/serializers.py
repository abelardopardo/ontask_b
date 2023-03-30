# -*- coding: UTF-8 -*-#

"""Classes to serialize Conditions."""
from typing import Optional

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from ontask import models
from ontask.column.serializers import ColumnNameSerializer
from ontask.dataops import formula

try:
    profile  # noqa: Z444
except NameError:
    def profile(bogus: int) -> int:
        """Useless, to prevent an emtpy exception handler"""
        return bogus  # noqa E731


def _create_condition(validated_data, context):
    """Create a new condition with the validated data.

    :param validated_data: Dictionary with the data validated by the serializer
    :param context: Dictionary with workflow, action, is_filter
    :return: reference to new condition object.
    """
    if context.get('is_filter', False):
        condition_obj = models.Filter(
            workflow=context['workflow'],
            action=context['action'],
            description_text=validated_data['description_text'],
            _formula=validated_data['_formula'],
            n_rows_selected=validated_data.get('n_rows_selected', -1))
        condition_obj.save()
    else:
        condition_obj = models.Condition(
            workflow=context['workflow'],
            action=context['action'],
            name=validated_data['name'],
            description_text=validated_data['description_text'],
            _formula=validated_data['_formula'],
            n_rows_selected=validated_data.get('n_rows_selected', -1))
        condition_obj.save()

    return condition_obj


class ConditionBaseSerializer(serializers.ModelSerializer):
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
            condition_obj = _create_condition(validated_data, self.context)

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
                self.context['workflow'].columns.filter(
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

        abstract = True
        exclude = (
            'id', 'workflow', 'action', 'created', 'modified', '_formula_text')

class ConditionSerializer(ConditionBaseSerializer):

    class Meta(ConditionBaseSerializer.Meta):
        """Define object condition and select fields to serialize."""

        model = models.Condition


class FilterSerializer(ConditionBaseSerializer):

    class Meta(ConditionBaseSerializer.Meta):
        """Define object condition and select fields to serialize."""

        model = models.Filter


class ConditionNameSerializer(serializers.ModelSerializer):
    """Trivial serializer to dump only the name of the column."""

    class Meta:
        """Select the model and the only field required."""

        model = models.Condition
        fields = ('name',)
