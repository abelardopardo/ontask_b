"""Views to manipulate the CRUD for scheduled executions."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import models
from ontask.core import (
    JSONFormResponseMixin, JSONResponseMixin, ScheduledOperationView,
    UserIsInstructor, WorkflowView, ajax_required, get_action,
    get_workflow, is_instructor, session_ops)
from ontask.scheduler import services


@method_decorator(ajax_required, name='dispatch')
class SchedulerIndexView(
    UserIsInstructor,
    JSONFormResponseMixin,
    WorkflowView,
    generic.DetailView
):
    model = models.ScheduledOperation
    template_name = 'scheduler/includes/partial_show_schedule_action.html'

    def get_queryset(self):
        # Consider only operations scheduled for this workflow
        return self.model.objects.filter(workflow=self.workflow)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            's_vals': services.get_item_value_dictionary(self.object),
            'timedelta': services.create_timedelta_string(
                self.object.execute_start,
                self.object.frequency,
                self.object.execute_until)})
        return context

    def get(self, request, *args, **kwargs):
        # Reset object to carry action info throughout dialogs
        session_ops.flush_payload(request)
        return super().get(request, *args, **kwargs)


@user_passes_test(is_instructor)
@get_action()
def create_action_run(
        request: http.HttpRequest,
        pk: int,
        workflow: Optional[models.Workflow] = None,
        action: Optional[models.Action] = None
) -> http.HttpResponse:
    """Create a new scheduled action run operation.

    :param request: HTTP request
    :param pk: primary key of the action
    :param workflow: Workflow of the current context.
    :param action: Action being used
    :return: HTTP response
    """
    # Remove the payload dictionary from the session
    session_ops.flush_payload(request)

    return services.SCHEDULE_CRUD_FACTORY.crud_view(
        request,
        action.action_type,
        workflow=workflow,
        action=action)


@user_passes_test(is_instructor)
@get_workflow()
def create_sql_upload(
        request: http.HttpRequest,
        pk: int,
        workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Create a new scheduled SQL upload operation.

    :param request: HTTP request
    :param pk: primary key of the action
    :param workflow: Workflow of the current context.
    :return: HTTP response
    """
    conn = False
    try:
        conn = models.SQLConnection.objects.filter(
            pk=pk).filter(enabled=True).first()
    except Exception:
        messages.error(request, 'Unable to retrieve connection.')

    if not conn:
        return redirect('scheduler:index')

    return services.SCHEDULE_CRUD_FACTORY.crud_view(
        request,
        models.Log.WORKFLOW_DATA_SQL_UPLOAD,
        workflow=workflow,
        connection=conn)


@user_passes_test(is_instructor)
@get_workflow()
def create_canvas_course_enrollment_upload(
        request: http.HttpRequest,
        workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Create a new Canvas Course Enrollment Update operation.

    :param request: HTTP request
    :param workflow: Workflow of the current context.
    :return: HTTP response
    """
    return services.SCHEDULE_CRUD_FACTORY.crud_view(
        request,
        models.Log.WORKFLOW_DATA_CANVAS_COURSE_ENROLLMENT_UPLOAD,
        workflow=workflow)


@user_passes_test(is_instructor)
@get_workflow()
def create_canvas_course_quizzes_upload(
        request: http.HttpRequest,
        workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Create a new Canvas Course Quizzes Update operation.

    :param request: HTTP request
    :param workflow: Workflow of the current context.
    :return: HTTP response
    """
    return services.SCHEDULE_CRUD_FACTORY.crud_view(
        request,
        models.Log.WORKFLOW_DATA_CANVAS_COURSE_QUIZZES_UPLOAD,
        workflow=workflow)


@user_passes_test(is_instructor)
@get_workflow()
def edit_scheduled_operation(
        request: http.HttpRequest,
        pk: int,
        workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Edit an existing scheduled email action.

    :param request: HTTP request
    :param pk: primary key of the action
    :param workflow: Workflow being manipulated.
    :return: HTTP response
    """
    s_item = workflow.scheduled_operations.filter(
        pk=pk).filter(
        Q(workflow__user=request.user)
        | Q(workflow__shared=request.user)).first()
    if not s_item:
        return redirect('home')

    # Remove the payload dictionary from the session
    session_ops.flush_payload(request)

    return services.SCHEDULE_CRUD_FACTORY.crud_view(
        request,
        s_item.operation_type,
        workflow=s_item.workflow,
        scheduled_item=s_item)


@user_passes_test(is_instructor)
@get_workflow()
def finish_scheduling(
        request: http.HttpRequest,
        workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Finish the create/edit operation of a scheduled operation."""
    payload = session_ops.get_payload(request)
    if payload is None or 'operation_type' not in payload:
        # Something is wrong with this execution. Return to action table.
        messages.error(
            request,
            _('Incorrect action scheduling invocation.'))
        return redirect('action:index')

    return services.SCHEDULE_CRUD_FACTORY.crud_view(
        request,
        payload.get('operation_type'),
        workflow=workflow,
        payload=payload,
        is_finish_request=True)


@method_decorator(ajax_required, name='dispatch')
class ScheduledItemDelete(
    UserIsInstructor,
    JSONFormResponseMixin,
    WorkflowView,
    generic.DeleteView,
):
    http_method_names = ['get', 'post']
    template_name = 'scheduler/includes/partial_scheduler_delete.html'

    def get_queryset(self):
        """Only obtain the scheduled actions in the current workflow."""
        return self.workflow.scheduled_operations.all()

    def form_valid(self, form):
        s_item = self.get_object()
        s_item.log(models.Log.SCHEDULE_DELETE)
        s_item.delete()
        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ActionToggleQuestionChangeView(
    UserIsInstructor,
    JSONResponseMixin,
    ScheduledOperationView
):
    """Enable/Disable a scheduled operation."""

    # Only AJAX Post requests allowed
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        sch_item = self.get_object()
        sch_item.task.enabled = not sch_item.task.enabled
        sch_item.task.save(update_fields=['enabled'])
        return http.JsonResponse({'is_checked': sch_item.task.enabled})
