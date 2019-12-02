# -*- coding: utf-8 -*-

"""View to implement the timeline visualization."""
import json
from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from ontask import models
from ontask.core.decorators import get_workflow
from ontask.core.permissions import is_instructor


@user_passes_test(is_instructor)
@get_workflow(pf_related='logs')
def show_timeline(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
) -> HttpResponse:
    """Show a vertical timeline of action executions.

    :param request: HTTP request
    :param pk: Action PK. If none, all of them in workflow are considered
    :param workflow: Workflow being manipulated (set by the decorators)
    :return: HTTP response
    """
    action = None
    if pk:
        action = workflow.actions.filter(pk=pk).first()

        if not action:
            # The action is not part of the selected workflow
            return redirect('home')
        logs = workflow.logs.filter(payload__action_id=action.id)
    else:
        logs = workflow.logs

    event_names = [
        models.Log.ACTION_DOWNLOAD,
        models.Log.ACTION_RUN_CANVAS_EMAIL,
        models.Log.ACTION_RUN_EMAIL,
        models.Log.ACTION_RUN_JSON,
        models.Log.ACTION_RUN_JSON_LIST,
        models.Log.ACTION_RUN_EMAIL_LIST,
        models.Log.ACTION_SURVEY_INPUT,
        models.Log.SCHEDULE_CANVAS_EMAIL_EDIT,
        models.Log.SCHEDULE_EMAIL_EDIT,
        models.Log.SCHEDULE_JSON_EDIT,
        models.Log.SCHEDULE_JSON_LIST_EDIT,
        models.Log.SCHEDULE_EMAIL_LIST_EDIT,
    ]

    # Filter the logs to display and transform into values (process the json
    # and the long value for the log name
    logs = [
        {'id': log.id,
         'name': log.get_name_display(),
         'modified': log.modified,
         'payload': json.dumps(log.payload, indent=2),
         'action_name': log.payload['action'],
         'action_id': log.payload['action_id']}
        for log in logs.filter(name__in=event_names)
    ]

    return render(
        request,
        'action/timeline.html',
        {'event_list': logs, 'action': action})
