# -*- coding: utf-8 -*-

"""Views to manipulate the CRUD for scheduled exections."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import redirect, reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _, ugettext_lazy as _

from ontask import models
from ontask.core import (
    SessionPayload, ajax_required, get_workflow, is_instructor,
)
from ontask.scheduler import services


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def view(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """View an existing scheduled action.

    :param request: HTTP request
    :param pk: primary key of the scheduled action
    :param workflow: Current workflow being used.
    :return: HTTP response
    """
    del request
    sch_obj = models.ScheduledOperation.objects.filter(
        workflow=workflow,
        pk=pk).first()
    if not sch_obj:
        # Connection object not found, go to table of sql connections
        return http.JsonResponse({'html_redirect': reverse('scheduler:index')})

    return http.JsonResponse({
        'html_form': render_to_string(
            'scheduler/includes/partial_show_schedule_action.html',
            {
                's_vals': services.get_item_value_dictionary(sch_obj),
                'id': sch_obj.id,
                'timedelta': services.create_timedelta_string(
                    sch_obj.execute,
                    sch_obj.frequency,
                    sch_obj.execute_until)})})


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def create_action_run(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Create a new scheduled action run operation.

    :param request: HTTP request
    :param pk: primary key of the action
    :param workflow: Workflow of the current context.
    :return: HTTP response
    """
    action = workflow.actions.filter(
        pk=pk).filter(
        Q(workflow__user=request.user)
        | Q(workflow__shared=request.user)).first()
    if not action:
        return redirect('home')

    return services.schedule_crud_factory.crud_process(
        action.action_type,
        action=action,
        schedule_item=None,
        request=request)


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
    except Exception as e:
        messages.error(request, 'Unable to retrieve connection.')

    if not conn:
        return redirect('scheduler:index')

    return services.schedule_crud_factory.crud_process(
        models.Log.WORKFLOW_DATA_SQL_UPLOAD,
        request=request,
        workflow=workflow,
        connection=conn,
        schedule_item=None)


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

    return services.schedule_crud_factory.crud_process(
        s_item.operation_type,
        request=request,
        schedule_item=s_item,
        workflow=s_item.workflow,
        action=s_item.action,
        prev_url=reverse(
            'scheduler:edit_scheduled_operation',
            kwargs={'pk': s_item.id}))


@user_passes_test(is_instructor)
@get_workflow()
def finish_scheduling(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Finish the create/edit operation of a scheduled operation."""
    del workflow
    payload = SessionPayload(request.session)
    if payload is None:
        # Something is wrong with this execution. Return to action table.
        messages.error(
            request,
            _('Incorrect action scheduling invocation.'))
        return redirect('action:index')

    return services.schedule_crud_factory.crud_finish(
        payload.get('operation_type'),
        request=request,
        payload=payload)


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related='actions')
def delete(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.JsonResponse:
    """View screen to confirm deletion scheduled item.

    :param request: Request object
    :param pk: Scheduled item id to delete
    :param workflow: workflow being manipulated.
    :return:
    """
    # Get the appropriate scheduled action
    s_item = workflow.scheduled_operations.filter(
        pk=pk).filter(
        Q(workflow__user=request.user)
        | Q(workflow__shared=request.user)).first()
    if not s_item:
        return http.JsonResponse({'html_redirect': reverse('scheduler:index')})

    if request.method == 'GET':
        return http.JsonResponse({
            'html_form': render_to_string(
                'scheduler/includes/partial_scheduler_delete.html',
                {'s_item': s_item},
                request=request),
        })

    services.delete_item(s_item)
    return http.JsonResponse({'html_redirect': reverse('scheduler:index')})


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def schedule_toggle(
    request: http.HttpRequest,
    pk: int,
    workflow: models.Workflow,
) -> http.JsonResponse:
    """Toggle the field enabled of a scheduled operation.

    :param request: HTML request object
    :param pk: Primary key of the scheduled element
    :return: JSON Response
    """
    del request
    sch_item = workflow.scheduled_operations.filter(pk=pk).first()
    if not sch_item:
        return http.JsonResponse({})

    sch_item.task.enabled = not sch_item.task.enabled
    sch_item.task.save(update_fields=['enabled'])
    return http.JsonResponse({'is_checked': sch_item.task.enabled})
