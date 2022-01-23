# -*- coding: utf-8 -*-

"""Functions to manipulate workflow CRUD ops."""
import copy
from typing import Dict

from django import http
from django.db.models.query_utils import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ontask import OnTaskServiceException, create_new_name, models
from ontask.action.services.clone import do_clone_action
from ontask.column.services import do_clone_column_only
from ontask.core import store_workflow_in_session
from ontask.dataops import sql
from ontask.table.services import do_clone_view
from ontask.workflow import forms


def log_workflow_createupdate(
    request: http.HttpRequest,
    workflow: models.Workflow,
    log_type: str,
) -> http.JsonResponse:
    """Log the workflow creation/update.

    :param request: Received HTTP Request
    :param workflow: Workflow being created/modified
    :param log_type: Type of operation (CREATE or UPDATE)
    :return: JSON Response
    """
    if log_type == models.Log.WORKFLOW_UPDATE:
        redirect_url = ''
    else:
        # This is a new instance!
        workflow.nrows = 0
        workflow.ncols = 0
        redirect_url = reverse('dataops:uploadmerge')

        # Store in session
        store_workflow_in_session(request.session, workflow)

    workflow.log(request.user, log_type)
    return http.JsonResponse({'html_redirect': redirect_url})


def do_clone_workflow(user, workflow: models.Workflow) -> models.Workflow:
    """Clone a workflow.

    :param user: User performing the operation
    :param workflow: source workflow
    :return: Cloned object
    """
    new_workflow = models.Workflow(
        user=workflow.user,
        name=create_new_name(
            workflow.name,
            models.Workflow.objects.filter(
                Q(user=workflow.user) | Q(shared=workflow.user)),
        ),
        description_text=workflow.description_text,
        nrows=workflow.nrows,
        ncols=workflow.ncols,
        attributes=copy.deepcopy(workflow.attributes),
        query_builder_ops=copy.deepcopy(workflow.query_builder_ops),
        luser_email_column_md5=workflow.luser_email_column_md5,
        lusers_is_outdated=workflow.lusers_is_outdated)
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

        # Clone the DB table
        if workflow.has_data_frame():
            sql.clone_table(
                workflow.get_data_frame_table_name(),
                new_workflow.get_data_frame_table_name())

        for item_obj in workflow.views.all():
            do_clone_view(user, item_obj, new_workflow)

        # Clone actions
        for item_obj in workflow.actions.all():
            do_clone_action(user, item_obj, new_workflow)

        # Done!
        new_workflow.save()
    except Exception as exc:
        raise OnTaskServiceException(
            message=_('Error while cloning workflow: {0}').format(exc),
            to_delete=[new_workflow])

    workflow.log(
        user,
        models.Log.WORKFLOW_CLONE,
        id_old=workflow.id,
        name_old=workflow.name)

    return new_workflow
