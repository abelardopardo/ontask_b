# -*- coding: utf-8 -*-

"""View to clone a workflow."""
import copy
import datetime
from typing import Optional

import pytz
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models.query_utils import Q
from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from action.views.clone import do_clone_action
from dataops.pandas import load_table, store_dataframe
from logs.models import Log
from ontask import create_new_name
from ontask.decorators import ajax_required, get_workflow
from ontask.permissions import is_instructor
from table.views.table_view import do_clone_view
from workflow.models import Column, Workflow


def do_clone_column(
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
            do_clone_column(item_obj, new_workflow=new_workflow)

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


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def clone(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Clone a workflow.

    :param request: HTTP request

    :param pk: Workflow id

    :return: JSON data
    """
    # Get the current workflow
    # Initial data in the context
    context = {'pk': wid, 'name': workflow.name}

    if request.method == 'GET':
        return JsonResponse({
            'html_form': render_to_string(
                'workflow/includes/partial_workflow_clone.html',
                context,
                request=request),
        })

    try:
        workflow_new = do_clone_workflow(workflow)
    except Exception as exc:
        messages.error(
            request,
            _('Unable to clone workflow: {0}').format(str(exc)),
        )
        return JsonResponse({'html_redirect': ''})

    # Log event
    Log.objects.register(
        request.user,
        Log.WORKFLOW_CLONE,
        workflow_new,
        {
            'id_old': workflow_new.id,
            'id_new': workflow.id,
            'name_old': workflow_new.name,
            'name_new': workflow.name})

    messages.success(
        request,
        _('Workflow successfully cloned.'))
    return JsonResponse({'html_redirect': ''})
