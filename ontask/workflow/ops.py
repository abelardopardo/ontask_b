# -*- coding: utf-8 -*-

"""Functions to perform various operations in a workflow."""
import copy
from typing import List, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext, ugettext_lazy as _

from ontask import create_new_name
from ontask.models import Condition
from ontask.dataops.pandas import load_table
from ontask.dataops.sql import (
    add_column_to_db, copy_column_in_db, df_drop_column, get_rows,
    is_column_unique,
)
from ontask.models import Log
from ontask.models import Column, Workflow

RANDOM_PWD_LENGTH = 50


def workflow_delete_column(
    workflow: Workflow,
    column: Column,
    cond_to_delete: Optional[List[Condition]] = None,
):
    """Remove column from ontask.workflow.

    Given a workflow and a column, removes it from the workflow (and the
    corresponding data frame

    :param workflow: Workflow object

    :param column: Column object to delete

    :param cond_to_delete: List of conditions to delete after removing the
    column

    :return: Nothing. Effect reflected in the database
    """
    # Drop the column from the DB table storing the data frame
    df_drop_column(workflow.get_data_frame_table_name(), column.name)

    # Reposition the columns above the one being deleted
    workflow.reposition_columns(column.position, workflow.ncols + 1)

    # Delete the column
    column.delete()

    # Update the information in the workflow
    workflow.ncols = workflow.ncols - 1
    workflow.save()

    if not cond_to_delete:
        # The conditions to delete are not given, so calculate them
        # Get the conditions/actions attached to this workflow
        cond_to_delete = [
            cond for cond in Condition.objects.filter(
                action__workflow=workflow,
            )
            if column in cond.columns.all()]

    # If a column disappears, the conditions that contain that variable
    # are removed
    actions_without_filters = []
    for condition in cond_to_delete:
        if condition.is_filter:
            actions_without_filters.append(condition.action)

        # Formula has the name of the deleted column. Delete it
        condition.delete()

    # Traverse the actions for which the filter has been deleted and reassess
    #  all their conditions
    # TODO: Explore how to do this asynchronously (or lazy)
    map(lambda act: act.update_n_rows_selected(), actions_without_filters)

    # If a column disappears, the views that contain only that column need to
    # disappear as well as they are no longer relevant.
    for view in workflow.views.all():
        if view.columns.count() == 0:
            view.delete()


def workflow_restrict_column(column: Column) -> Optional[str]:
    """Set category of the column to the existing set of values.

    Given a workflow and a column, modifies the column so that only the
    values already present are allowed for future updates.

    :param column: Column object to restrict

    :return: String with error or None if correct
    """
    # Load the data frame
    data_frame = load_table(
        column.workflow.get_data_frame_table_name())

    cat_values = set(data_frame[column.name].dropna())
    if not cat_values:
        # Column has no meaningful values. Nothing to do.
        return _('Column has no meaningful values')

    # Set categories
    column.set_categories(list(cat_values))
    column.save()

    # Re-evaluate the operands in the workflow
    column.workflow.set_query_builder_ops()
    column.workflow.save()

    # Correct execution
    return None


def do_workflow_update_lusers(workflow: Workflow, log_item: Log):
    """Recalculate the field lusers.

    Recalculate the elements in the field lusers of the workflow based on the
    fields luser_email_column and luser_email_column_MD5

    :param workflow: Workflow to update

    :param log_item: Log where to leave the status of the operation

    :return: Changes in the lusers ManyToMany relationships
    """
    # Get the column content
    emails = get_rows(
        workflow.get_data_frame_table_name(),
        column_names=[workflow.luser_email_column.name])

    luser_list = []
    created = 0
    for row in emails:
        uemail = row[workflow.luser_email_column.name]
        luser = get_user_model().objects.filter(email=uemail).first()
        if not luser:
            # Create user
            if settings.DEBUG:
                # Define users with the same password in development
                password = 'boguspwd'  # NOQA
            else:
                password = get_random_string(length=RANDOM_PWD_LENGTH)
            luser = get_user_model().objects.create_user(
                email=uemail,
                password=password,
            )
            created += 1

        luser_list.append(luser)

    # Assign result
    workflow.lusers.set(luser_list)

    # Report status
    log_item.payload['total_users'] = emails.rowcount
    log_item.payload['new_users'] = created
    log_item.payload['status'] = ugettext(
        'Learner emails successfully updated.',
    )
    log_item.save()


def do_clone_column_only(
    column: Column,
    new_workflow: Optional[Workflow] = None,
    new_name: Optional[str] = None,
) -> Column:
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

    new_column = Column(
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


def clone_wf_column(column: Column) -> Column:
    """Create a clone of a column.

    :param column: Object to clone

    :return: Cloned object (DF has an additional column as well
    """
    workflow = column.workflow

    new_column = do_clone_column_only(
        column,
        new_name=create_new_name(column.name, workflow.columns))

    # Update the number of columns in the workflow
    workflow.ncols += 1
    workflow.save()
    workflow.refresh_from_db()

    # Reposition the new column at the end
    new_column.position = workflow.ncols
    new_column.save()

    # Create the column in the database
    add_column_to_db(
        workflow.get_data_frame_table_name(),
        new_column.name,
        new_column.data_type)

    copy_column_in_db(
        workflow.get_data_frame_table_name(),
        column.name,
        new_column.name)

    return new_column


def check_key_columns(workflow: Workflow):
    """Check that key columns maintain their property.

    Function used to verify that after changes in the DB the key columns
    maintain their property.

    :param workflow: Object to use for the verification.

    :return: Nothing. Raise exception if key column lost the property.
    """
    col_name = next(
        (col.name for col in workflow.columns.filter(is_key=True)
         if not is_column_unique(
            workflow.get_data_frame_table_name(), col.name)),
        None)
    if col_name:
        raise Exception(_(
            'The new data does not preserve the key '
            + 'property of column "{0}"'.format(col_name)))
