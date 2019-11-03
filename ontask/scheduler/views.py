# -*- coding: utf-8 -*-

"""Views to manipulate the CRUD for scheduled exections."""
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect, render, reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.action import payloads
from ontask.core import SessionPayload
from ontask.core.decorators import ajax_required, get_workflow
from ontask.core.permissions import is_instructor
from ontask.scheduler import services


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def index(
    request: HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> HttpResponse:
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


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def view(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> JsonResponse:
    """View an existing scheduled action.

    :param request: HTTP request

    :param pk: primary key of the scheduled action

    :param workflow: Current workflow being used.
    :return: HTTP response
    """
    del request

    sch_obj = models.ScheduledOperation.objects.filter(
        action__workflow=workflow,
        pk=pk).first()
    if not sch_obj:
        # Connection object not found, go to table of sql connections
        return JsonResponse({'html_redirect': reverse('scheduler:index')})

    return JsonResponse({
        'html_form': render_to_string(
            'scheduler/includes/partial_show_schedule_action.html',
            {
                's_vals': services.get_item_value_dictionary(sch_obj),
                'id': sch_obj.id,
                'timedelta': services.create_timedelta_string(
                    sch_obj.execute,
                    sch_obj.execute_until),
            },
        ),
    })


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def create_action_run(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> HttpResponse:
    """Edit an existing scheduled action run operation.

    :param request: HTTP request

    :param pk: primary key of the action

    :param workflow: Workflow of the current context.
    :return: HTTP response
    """
    action = workflow.actions.filter(
        pk=pk
    ).filter(
        Q(workflow__user=request.user)
        | Q(workflow__shared=request.user),
    ).first()
    if not action:
        return redirect('home')

    return services.schedule_crud_factory.crud_process(
        models.scheduler.RUN_ACTION,
        action=action,
        schedule_item=None,
        request=request,
        prev_url=reverse(
            'scheduler:create_action_run',
            kwargs={'pk': action.id}))

@user_passes_test(is_instructor)
@get_workflow()
def edit_scheduled_operation(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> HttpResponse:
    """Edit an existing scheduled email action.

    :param request: HTTP request

    :param pk: primary key of the action

    :return: HTTP response
    """
    s_item = workflow.scheduled_operations.filter(
        pk=pk
    ).filter(
        Q(workflow__user=request.user)
        | Q(workflow__shared=request.user)
    ).first()
    if not s_item:
        return redirect('home')

    return services.schedule_crud_factory.crud_process(
        models.scheduler.RUN_ACTION,
        request=request,
        action=s_item.action,
        schedule_item=s_item,
        prev_url=reverse(
            'scheduler:edit_scheduled_operation',
            kwargs={'pk': s_item.id}))


@user_passes_test(is_instructor)
@get_workflow()
def create_workflow_op(
    request: HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> HttpResponse:
    """Create a new workflow operation."""
    del workflow
    messages.error(
        request,
        _('Under implementation'))
    return redirect('scheduler:index')


@user_passes_test(is_instructor)
@get_workflow()
def finish_scheduling(
    request: HttpRequest,
    workflow: Optional[models.Workflow] = None
) -> HttpResponse:
    """Finish the create/edit operation of a scheduled operation"""
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
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> JsonResponse:
    """View screen to confirm deletion scheduled item.

    :param request: Request object

    :param pk: Scheduled item id to delete

    :return:
    """
    # Get the appropriate scheduled action
    s_item = workflow.scheduled_operations.filter(
        pk=pk
    ).filter(
        Q(workflow__user=request.user)
        | Q(workflow__shared=request.user)
    ).first()
    if not s_item:
        return JsonResponse({'html_redirect': reverse('scheduler:index')})

    if request.method == 'GET':
        return JsonResponse({
            'html_form': render_to_string(
                'scheduler/includes/partial_scheduler_delete.html',
                {'s_item': s_item},
                request=request),
        })

    services.delete_item(s_item)
    return JsonResponse({'html_redirect': reverse('scheduler:index')})
