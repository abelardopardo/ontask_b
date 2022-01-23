# -*- coding: utf-8 -*-

"""Views to show logs and log table."""

from django import http
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask.core import (
    JSONFormResponseMixin, LogView, UserIsInstructor, WorkflowView,
    ajax_required)
from ontask.logs import services


class LogIndexView(UserIsInstructor, WorkflowView, generic.TemplateView):
    """Render the table frame for the logs."""

    http_method_names = ['get']
    template_name = 'logs/display.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'workflow': self.workflow,
            'column_names': [
                _('ID'),
                _('Event type'),
                _('Date/Time'),
                _('User')]})
        return context


@method_decorator(ajax_required, name='dispatch')
class LogIndexSSView(UserIsInstructor, WorkflowView):
    """Render the server side page for the table of columns."""

    http_method_names = ['post']
    wf_pf_related = 'logs'

    def post(self, request, *args, **kwargs):
        return http.JsonResponse(
            services.log_table_server_side(request, self.workflow))


@method_decorator(ajax_required, name='dispatch')
class LogDetailModalView(
    UserIsInstructor,
    JSONFormResponseMixin,
    LogView,
    generic.DetailView
):
    """View the content of one of the logs in a modal."""

    http_method_names = ['get']
    template_name = 'logs/includes/partial_show.html'
    s_related = 'workflow'


class LogDetailView(UserIsInstructor, LogView, generic.DetailView):
    """View the content of one of the logs."""

    template_name = 'logs/view.html'
    s_related = 'workflow'


class LogExportView(UserIsInstructor, WorkflowView):
    """Export the logs from the given workflow."""

    http_method_names = ['get']
    wf_pf_related = 'logs'

    def get(self, request, *args, **kwargs):
        dataset = services.LogResource().export(
            self.workflow.logs.filter(user=request.user))

        # Create the response as a csv download
        response = http.HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="logs.csv"'

        return response
