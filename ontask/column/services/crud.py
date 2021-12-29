# -*- coding: utf-8 -*-

"""Functions to manipulate column CRUD ops."""
import copy
import random
from typing import Any, List, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import pandas as pd

from ontask import create_new_name, models
from ontask.column.services import errors
from ontask.dataops import pandas, sql

_op_distrib = {
    'sum': lambda operand: operand.sum(axis=1, skipna=False),
    'prod': lambda operand: operand.prod(axis=1, skipna=False),
    'max': lambda operand: operand.max(axis=1, skipna=False),
    'min': lambda operand: operand.min(axis=1, skipna=False),
    'mean': lambda operand: operand.mean(axis=1, skipna=False),
    'median': lambda operand: operand.median(axis=1, skipna=False),
    'std': lambda operand: operand.std(axis=1, skipna=False),
    'all': lambda operand: operand.all(axis=1, skipna=False),
    'any': lambda operand: operand.any(axis=1, skipna=False),
}

_ontask_type_to_pd_type = {
    'string': 'object',
    'integer': 'int64',
    'double':  'float64',
    'boolean': 'bool',
    'datetime': 'datetime64[ns, {0}]'.format(settings.TIME_ZONE)}


def _partition(list_in: List[Any], num: int) -> List[List[Any]]:
    """Partitions the list in num lists.

    Given a list and n, returns a list with n lists, and inside each of them a
    set of elements from the shuffled list. All lists are of the same size

    :param list_in: List of elements to partition
    :param num: Number of partitions
    :return: List of lists with shuffled elements partitioned
    """
    random.shuffle(list_in)
    return [list_in[idx::num] for idx in range(num)]


def add_column_to_workflow(
    user,
    workflow: models.Workflow,
    column: models.Column,
    column_initial_value: Any,
    action_column_event: Optional[str] = None,
    action: Optional[models.Action] = None,
):
    """Add a new column to the workflow.

    :param user: User executing the operation
    :param workflow: Used workflow
    :param column: Column to insert
    :param column_initial_value: Initial value for the column
    :param action_column_event: Event to record if the action/column needs to
    be stored
    :param action: If the column is a question, this is the action in which it
    is being used.
    :return: Nothing. Column added to Wflow and DB
    """
    # Catch the special case of integer type and no initial value. Pandas
    # encodes it as NaN but a cycle through the database transforms it into
    # a string. To avoid this case, integer + empty value => double
    if column.data_type == 'integer' and column_initial_value is None:
        column.data_type = 'double'

    # Fill in the remaining fields in the column
    column.workflow = workflow
    column.is_key = False

    # Add the new column to the DB
    try:
        sql.add_column_to_db(
            workflow.get_data_frame_table_name(),
            column.name,
            column.data_type,
            initial=column_initial_value)
    except Exception as exc:
        raise errors.OnTaskColumnAddError(
            message=_('Unable to add element: {0}').format(str(exc)))

    # Update the positions of the appropriate columns
    workflow.reposition_columns(workflow.ncols + 1, column.position)

    # Save column, refresh workflow, and increase number of columns
    column.save()
    workflow.refresh_from_db()
    workflow.ncols += 1
    workflow.set_query_builder_ops()
    workflow.save(update_fields=['ncols', 'query_builder_ops'])

    if action_column_event:
        acc, __ = models.ActionColumnConditionTuple.objects.get_or_create(
            action=action,
            column=column,
            condition=None)
        acc.log(user, action_column_event)
    column.log(user, models.Log.COLUMN_ADD)


def add_formula_column(
    user,
    workflow: models.Workflow,
    column: models.Column,
    operation: str,
    selected_columns: List[models.Column],
):
    """Add the formula column to the workflow.

    :param user: User making the request
    :param workflow: Workflow to add the column
    :param column: Column being added
    :param operation: string denoting the operation
    :param selected_columns: List of columns selected for the operation.
    :return: Column is added to the workflow
    """
    # Save the column object attached to the form and add additional fields
    column.workflow = workflow
    column.is_key = False

    # Save the instance
    column.save()

    # Update the data frame
    df = pandas.load_table(workflow.get_data_frame_table_name())

    # Add the column with the appropriate computation
    cnames = [col.name for col in selected_columns]
    df[column.name] = _op_distrib[operation](df[cnames])

    # Populate the column type
    column.data_type = pandas.datatype_names.get(
        df[column.name].dtype.name)

    # Update the positions of the appropriate columns
    workflow.reposition_columns(workflow.ncols + 1, column.position)
    column.save()
    workflow.refresh_from_db()

    # Store the df to DB
    try:
        pandas.store_dataframe(df, workflow)
    except Exception as exc:
        raise errors.OnTaskColumnAddError(
            message=_('Unable to add column: {0}').format(str(exc)),
            to_delete=[column])

    workflow.ncols = workflow.columns.count()
    workflow.set_query_builder_ops()
    workflow.save(update_fields=['ncols', 'query_builder_ops'])
    column.log(user, models.Log.COLUMN_ADD_FORMULA)


def add_random_column(
    user,
    workflow: models.Workflow,
    column: models.Column,
    data_frame: pd.DataFrame,
):
    """Add the formula column to the workflow.

    :param user: User making the request
    :param workflow: Workflow to add the column
    :param column: Column being added
    :param data_frame: Data frame of the current workflow
    :return: Column is added to the workflow
    """
    # Empty new column
    new_column = [None] * workflow.nrows
    categories = column.get_categories()
    # Create the random partitions
    partitions = _partition(
        [idx for idx in range(workflow.nrows)],
        len(categories))

    # Assign values to partitions
    for idx, indexes in enumerate(partitions):
        for col_idx in indexes:
            new_column[col_idx] = categories[idx]

    # Assign the new column to the data frame
    data_frame[column.name] = pd.Series(
        new_column,
        dtype=_ontask_type_to_pd_type[column.data_type],
        index=data_frame.index)

    if column.data_type == 'datetime' and data_frame[column.name].dt.tz is None:
        data_frame[column.name] = data_frame[column.name].dt.tz_localize(
            settings.TIME_ZONE)

    # Update the positions of the appropriate columns
    workflow.reposition_columns(workflow.ncols + 1, column.position)
    workflow.refresh_from_db()

    # Store the df to DB
    try:
        pandas.store_dataframe(data_frame, workflow)
    except Exception as exc:
        raise errors.OnTaskColumnAddError(
            message=_('Unable to add the column: {0}').format(str(exc)),
            to_delete=[column])

    workflow.ncols = workflow.columns.count()
    workflow.set_query_builder_ops()
    workflow.save(update_fields=['ncols', 'query_builder_ops'])

    # Log the event
    column.log(user, models.Log.COLUMN_ADD_RANDOM)


def update_column(
    user,
    workflow: models.Workflow,
    column: models.Column,
    old_name: str,
    old_position: int,
    action_column_item: Optional[models.Action] = None,
    action_column_event: Optional[str] = None,
):
    """Update information in a column.

    :param user: User performing the operation
    :param workflow: Workflow being processed
    :param column: Column being modified
    :param old_name: Old name to detect renaming
    :param old_position: old position to detect repositioning
    :param action_column_item: Action/column item in case the action is stored
    in that table.
    :param action_column_event: Event to record the operation on the
    action/column
    :return: Nothing. Side effect in the workflow.
    """
    # If there is a new name, rename the data frame columns
    if old_position != column.position:
        # Update the positions of the appropriate columns
        workflow.reposition_columns(old_position, column.position)

    if old_name != column.name:
        sql.db_rename_column(
            workflow.get_data_frame_table_name(),
            old_name,
            column.name)

    column.save()

    # Go back to the DB because the prefetch columns are not valid
    # any more
    workflow = models.Workflow.objects.prefetch_related('columns').get(
        id=workflow.id,
    )

    # Propagate the rename to the other actions and views
    if old_name != column.name:
        pandas.rename_column(workflow, old_name, column.name)

    # Changes in column require rebuilding the query_builder_ops
    workflow.set_query_builder_ops()
    workflow.save(update_fields=['query_builder_ops'])

    if action_column_item:
        action_column_item.log(user, action_column_event)

    # Log the event
    column.log(user, models.Log.COLUMN_EDIT)


def delete_column(
    user: get_user_model(),
    workflow: models.Workflow,
    column: models.Column,
):
    """Remove column from ontask.workflow.

    Given a workflow and a column, removes it from the workflow (and the
    corresponding data frame). All conditions and filters that use that column
    need to be removed as well.

    :param user: User performing the operation
    :param workflow: Workflow object
    :param column: Column object to delete
    :return: Nothing. Effect reflected in the database
    """
    column.log(user, models.Log.COLUMN_DELETE)

    # Drop the column from the DB table storing the data frame
    sql.df_drop_column(workflow.get_data_frame_table_name(), column.name)

    # Reposition the columns above the one being deleted
    workflow.reposition_columns(column.position, workflow.ncols + 1)

    # Delete the column
    column.delete()

    # Update the information in the workflow
    workflow.ncols = workflow.ncols - 1
    workflow.save(update_fields=['ncols'])

    # Delete the conditions with this column
    cond_to_delete = workflow.conditions.filter(columns=column)
    for cond in cond_to_delete:
        # Set rows_all_false to None as it now contains the wrong number
        cond.action.rows_all_false = None
        cond.action.save(update_fields=['rows_all_false'])
    cond_to_delete.delete()

    # Delete the filters
    workflow.filters.filter(columns=column).delete()

    # If a column disappears, the views that contain only that column need to
    # disappear as well as they are no longer relevant.
    for view in workflow.views.all():
        if view.columns.count() == 0:
            view.delete()
            continue

        # Views that loose the key column must be deleted as well
        if view.columns.filter(is_key=True).count() == 0:
            view.delete()


def clone_column(user, column: models.Column) -> models.Column:
    """Create a clone of a column.

    :param user: User executing operation
    :param column: Object to clone
    :return: Cloned object (DF has an additional column as well
    """
    workflow = column.workflow

    new_column = do_clone_column_only(
        column,
        new_name=create_new_name(column.name, workflow.columns))

    # Update the number of columns in the workflow
    workflow.ncols += 1
    workflow.save(update_fields=['ncols'])
    workflow.refresh_from_db()

    # Reposition the new column at the end
    new_column.position = workflow.ncols
    new_column.save()

    # Create the column in the database
    sql.add_column_to_db(
        workflow.get_data_frame_table_name(),
        new_column.name,
        new_column.data_type)

    sql.copy_column_in_db(
        workflow.get_data_frame_table_name(),
        column.name,
        new_column.name)

    new_column.log(user, models.Log.COLUMN_CLONE)

    return new_column


def do_clone_column_only(
    column: models.Column,
    new_workflow: Optional[models.Workflow] = None,
    new_name: Optional[str] = None,
) -> models.Column:
    """Clone a column.

    :param column: Object to clone.
    :param new_workflow: Optional new worklow object to link to.
    :param new_name: Optional new name to use.
    :result: New object.
    """
    if new_name is None:
        new_name = column.name
    if new_workflow is None:
        new_workflow = column.workflow

    new_column = models.Column(
        name=new_name,
        description_text=column.description_text,
        workflow=new_workflow,
        data_type=column.data_type,
        is_key=column.is_key,
        position=column.position,
        in_viz=column.in_viz,
        categories=copy.deepcopy(column.categories),
        active_from=column.active_from,
        active_to=column.active_to,
    )
    new_column.save()
    return new_column
