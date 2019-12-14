# -*- coding: utf-8 -*-

"""Index of scheduled operations."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from ontask import models
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
                models.ScheduledOperation.objects.filter(
                    action__workflow=workflow.id),
                orderable=False),
            'workflow': workflow,
        },
    )
