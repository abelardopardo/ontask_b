# -*- coding: utf-8 -*-

"""Views to flush, show details, column server side, etc."""

from django import http
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from ontask import OnTaskServiceException, models
from ontask.core import (
    JSONFormResponseMixin, SingleWorkflowMixin, UserIsInstructor,
    RequestWorkflowView, ajax_required, error_redirect)
from ontask.workflow import services


@method_decorator(ajax_required, name='dispatch')
class WorkflowFlushView(
    UserIsInstructor,
    SingleWorkflowMixin,
    JSONFormResponseMixin,
    generic.DetailView
):
    """View to flush a workflow."""

    http_method_names = ['get', 'post']
    template_name = 'workflow/includes/partial_workflow_flush.html'

    def post(self, request, *args, **kwargs):
        """Perform the flush operation."""

        workflow = self.get_object()
        if workflow.nrows != 0:
            services.do_flush(request, workflow)
        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class WorkflowStar(
    UserIsInstructor,
    SingleWorkflowMixin,
    JSONFormResponseMixin,
    generic.View
):
    """Start a workflow."""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        """Add/Remove star and log operation"""

        self.object = self.get_object()

        # Get the workflows with stars
        stars = request.user.workflows_star.all()
        if self.object in stars:
            self.object.star.remove(request.user)
        else:
            self.object.star.add(request.user)

        self.object.log(request.user, models.Log.WORKFLOW_STAR)
        return http.JsonResponse({})


class WorkflowOperationsView(
    UserIsInstructor,
    SingleWorkflowMixin,
    generic.DetailView
):
    """View workflow operations page."""

    http_method_names = ['get']
    template_name = 'workflow/operations.html'
    s_related = 'luser_email_column'
    pf_related = ['columns', 'shared']

    def get_context_data(self, **kwargs):
        """Add all elements required to view the operations."""
        context = super().get_context_data(**kwargs)

        workflow = context['object']
        context.update({
            'attribute_table': services.AttributeTable([
                {'id': idx, 'name': key, 'value': kval}
                for idx, (key, kval) in enumerate(sorted(
                    workflow.attributes.items()))],
                orderable=False),
            'share_table': services.WorkflowShareTable(
                workflow.shared.values('email', 'id').order_by('email')),
            'unique_columns': workflow.get_unique_columns()})

        return context

    def get(self, request, *args, **kwargs):
        """Render the operations page."""

        try:
            self.object = self.get_object()

            # Check if lusers is active and if so, if it needs to be refreshed
            services.check_luser_email_column_outdated(self.object)
        except Exception as exc:
            return error_redirect(request, message=str(exc))

        return self.render_to_response(
            self.get_context_data(object=self.object))


@method_decorator(ajax_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class WorkflowAssignLUserColumn(
    UserIsInstructor,
    JSONFormResponseMixin,
    RequestWorkflowView,
):
    """Assign the value of the LUser column."""

    # Only AJAX Post requests allowed
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """Assign the LUser column (if present)."""

        if self.workflow.nrows == 0:
            messages.error(
                request,
                _(
                    'Workflow has no data. '
                    + 'Go to "Manage table data" to upload data.'))
            return http.JsonResponse({'html_redirect': reverse('action:index')})

        pk = kwargs.get('pk')
        column = None

        try:
            if pk:
                column = self.workflow.columns.filter(
                        pk=pk,
                    ).filter(
                        Q(workflow__user=request.user)
                        | Q(workflow__shared=request.user),
                    ).distinct().get()
            services.update_luser_email_column(
                request.user,
                pk,
                self.workflow,
                column)
            messages.success(
                request,
                _('The list of workflow users will be updated shortly.'),
            )
        except OnTaskServiceException as exc:
            exc.message_to_error(request)

        return http.JsonResponse({'html_redirect': ''})
