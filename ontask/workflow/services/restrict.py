# -*- coding: utf-8 -*-

"""Function to restrict column values."""
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.dataops import pandas
from ontask.workflow import services


def restrict_column(user, column: models.Column):
    """Set category of the column to the existing set of values.

    Given a workflow and a column, modifies the column so that only the
    values already present are allowed for future updates.

    :param user: User executing this action
    :param column: Column object to restrict
    :return: String with error or None if correct
    """
    # Load the data frame
    data_frame = pandas.load_table(
        column.workflow.get_data_frame_table_name())

    cat_values = set(data_frame[column.name].dropna())
    if not cat_values:
        raise services.OnTaskWorkflowNoCategoryValues(
            message=_('The column has no meaningful values'))

    # Set categories
    column.set_categories(list(cat_values))
    column.save()

    # Re-evaluate the operands in the workflow
    column.log(user, models.Log.COLUMN_RESTRICT)
    column.workflow.set_query_builder_ops()
    column.workflow.save()
