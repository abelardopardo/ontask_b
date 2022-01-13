# -*- coding: utf-8 -*-

"""Views to show logs and log table."""

from django import http
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from ontask import models
from ontask.core import (
    JSONFormResponseMixin, UserIsInstructor, WorkflowView, ajax_required)
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
@method_decorator(csrf_exempt, name='dispatch')
class LogIndexSSView(UserIsInstructor, WorkflowView):
    """Render the server side page for the table of columns."""

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        return http.JsonResponse(
            services.log_table_server_side(request, self.workflow))


class LogDetailBasicView(
    UserIsInstructor,
    WorkflowView,
    generic.DetailView
):
    """Basic class to view the content of one of the logs."""

    model = models.Log
    http_method_names = ['get']

    def get_queryset(self):
        """Consider only logs in this workflow."""
        return self.workflow.logs.filter(user=self.request.user)


@method_decorator(ajax_required, name='dispatch')
class LogDetailModalView(LogDetailBasicView, JSONFormResponseMixin):
    """View the content of one of the logs in a modal."""

    template_name = 'logs/includes/partial_show.html'


class LogDetailView(LogDetailBasicView):
    """View the content of one of the logs."""

    template_name = 'logs/view.html'


class LogExportView(UserIsInstructor, WorkflowView):
    """Export the logs from the given workflow."""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        dataset = services.LogResource().export(
            self.workflow.logs.filter(user=request.user))

        # Create the response as a csv download
        response = http.HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="logs.csv"'

        return response
