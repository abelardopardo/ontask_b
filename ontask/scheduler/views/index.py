# -*- coding: utf-8 -*-

"""Index of scheduled operations."""

from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import models
from ontask.connection.services import create_sql_connection_runtable
from ontask.core import (
    SessionPayload, UserIsInstructor, WorkflowView)
from ontask.scheduler import services


class SchedulerIndex(UserIsInstructor, WorkflowView, generic.TemplateView):
    """Render the list of scheduled actions in the workflow."""

    template_name = 'scheduler/index.html'
    wf_pf_related = 'actions'

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
