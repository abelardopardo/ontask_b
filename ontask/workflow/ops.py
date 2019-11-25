# -*- coding: utf-8 -*-

"""Functions to perform various operations in a workflow."""
import copy
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext, ugettext_lazy as _

from ontask.dataops.sql import (
    get_rows,
    is_column_unique,
)
from ontask.models import Column, Log, Workflow

RANDOM_PWD_LENGTH = 50


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
    workflow.lusers_is_outdated = False
    workflow.save()

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
