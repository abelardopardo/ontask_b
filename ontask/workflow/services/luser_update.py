# -*- coding: utf-8 -*-

"""Functions to support task execcution for workflows."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext

from ontask import models
from ontask.dataops.sql import get_rows

RANDOM_PWD_LENGTH = 50


def do_workflow_update_lusers(workflow: models.Workflow, log_item: models.Log):
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
