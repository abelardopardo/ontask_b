"""Function to restrict column values."""
from django.utils.translation import gettext_lazy as _

from ontask import models
from ontask.column.services import errors
from ontask.dataops import sql


def restrict_column(user, column: models.Column):
    """Set category of the column to the existing set of values.

    Given a workflow and a column, modifies the column so that only the
    values already present are allowed for future updates.

    :param user: User executing this action
    :param column: Column object to restrict
    :return: String with error or None if correct
    """
    cat_values = sql.get_column_distinct_values(
        column.workflow.get_data_frame_table_name(),
        column.name)
    if not cat_values:
        raise errors.OnTaskColumnCategoryValueError(
            message=_('The column has no meaningful values'))

    # Set categories
    column.set_categories(cat_values)

    # Re-evaluate the operands in the workflow
    column.log(user, models.Log.COLUMN_RESTRICT)
    column.workflow.set_query_builder_ops()
    column.workflow.save()
