# -*- coding: utf-8 -*-

"""Index of scheduled operations."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.connection.services import sql_connection_select_table
from ontask.core import SessionPayload, get_workflow, is_instructor
from ontask.scheduler import services


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def index(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Render the list of actions attached to a workflow.

    :param request: Request object
    :param workflow: Workflow currently used
    :return: HTTP response with the table.
    """
    # Reset object to carry action info throughout dialogs
    SessionPayload.flush(request.session)

    return render(
        request,
        'scheduler/index.html',
        {
            'table': services.ScheduleActionTable(
                models.ScheduledOperation.objects.filter(workflow=workflow.id),
                orderable=False),
            'workflow': workflow})


@user_passes_test(is_instructor)
@get_workflow()
def sql_connection_index(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Show table of SQL connections for user to choose one.

    :param request: HTTP request
    :param workflow: Workflow of the current context.
    :return: HTTP response
    """
    del workflow
    table = sql_connection_select_table('scheduler:sqlupload')
    return render(
        request,
        'connection/index.html',
        {'table': table, 'is_sql': True, 'title': _('SQL Connections')})
