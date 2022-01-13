# -*- coding: utf-8 -*-

"""Index of scheduled operations."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import models
from ontask.connection.services import create_sql_connection_runtable
from ontask.core import (
    SessionPayload, UserIsInstructor, WorkflowView,
    get_workflow, is_instructor)
from ontask.scheduler import services


class SchedulerIndex(UserIsInstructor, WorkflowView, generic.TemplateView):
    """Render the list of scheduled actions in the workflow."""

    template_name = 'scheduler/index.html'
    pf_related = 'actions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = services.ScheduleActionTable(
            models.ScheduledOperation.objects.filter(
                workflow=self.workflow.id),
            orderable=False)
        return context

    def get(self, request, *args, **kwargs):
        # Reset object to carry action info throughout dialogs
        SessionPayload.flush(request.session)

        return super().get(request, *args, **kwargs)


class SchedulerConnectionIndex(
    UserIsInstructor,
    WorkflowView,
    generic.TemplateView
):
    """Show table of SQL connections for user to choose one."""

    template_name = 'connection/index.html'
    title = _('SQL Connections')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = create_sql_connection_runtable('scheduler:sqlupload')
        return context

    def get(self, request, *args, **kwargs):
        # Reset object to carry action info throughout dialogs
        SessionPayload.flush(request.session)

        return super().get(request, *args, **kwargs)


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
    table = create_sql_connection_runtable('scheduler:sqlupload')
    return render(
        request,
        'connection/index.html',
        {'table': table, 'is_sql': True, 'title': _('SQL Connections')})
