# -*- coding: utf-8 -*-

"""Functions to perform various operations in a workflow."""
import copy
from typing import List, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.query_utils import Q
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext, ugettext_lazy as _

from action.models import Condition
from action.views.clone import do_clone_action
from dataops.pandas import load_table, store_dataframe
from dataops.sql.column_queries import df_drop_column
from dataops.sql.row_queries import get_rows
from logs.models import Log
from ontask import create_new_name
from table.views.table_view import do_clone_view
from workflow.models import Column, Workflow

RANDOM_PWD_LENGTH = 50


def workflow_delete_column(
    workflow: Workflow,
    column: Column,
    cond_to_delete: Optional[List[Condition]] = None,
):
    """Remove column from workflow.

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
    for action in actions_without_filters:
        action.update_n_rows_selected()

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
    log_item.payload['total_users'] = len(emails)
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


def clone_wf_df_column(column: Column) -> Column:
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

    # Add the column to the table and update it.
    data_frame = load_table(
        workflow.get_data_frame_table_name())
    data_frame[new_column.name] = data_frame[column.name]
    store_dataframe(data_frame, workflow)

    return new_column


def do_clone_workflow(workflow: Workflow) -> Workflow:
    """Clone the workflow.

    :param workflow: source workflow

    :return: Clone object
    """
    new_workflow = Workflow(
        user=workflow.user,
        name=create_new_name(
            workflow.name,
            Workflow.objects.filter(
                Q(user=workflow.user) | Q(shared=workflow.user)),
        ),
        description_text=workflow.description_text,
        nrows=workflow.nrows,
        ncols=workflow.ncols,
        attributes=copy.deepcopy(workflow.attributes),
        query_builder_ops=copy.deepcopy(workflow.query_builder_ops),
        luser_email_column_md5=workflow.luser_email_column_md5,
        lusers_is_outdated=workflow.lusers_is_outdated
    )
    new_workflow.save()
    try:
        new_workflow.shared.set(list(workflow.shared.all()))
        new_workflow.lusers.set(list(workflow.lusers.all()))

        # Clone the columns
        for item_obj in workflow.columns.all():
            do_clone_column_only(item_obj, new_workflow=new_workflow)

        # Update the luser_email_column if needed:
        if workflow.luser_email_column:
            new_workflow.luser_email_column = new_workflow.columns.get(
                name=workflow.luser_email_column.name,
            )

        # Clone the data frame
        data_frame = load_table(workflow.get_data_frame_table_name())
        store_dataframe(data_frame, new_workflow)

        # Clone actions
        for item_obj in workflow.actions.all():
            do_clone_action(item_obj, new_workflow)

        for item_obj in workflow.views.all():
            do_clone_view(item_obj, new_workflow)

        # Done!
        new_workflow.save()
    except Exception as exc:
        new_workflow.delete()
        raise exc

    return new_workflow
