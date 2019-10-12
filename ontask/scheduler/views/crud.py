# -*- coding: utf-8 -*-

"""Views to manipulate the CRUD for scheduled exections."""

import json
from builtins import object
from typing import Optional

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django_tables2 import A

from ontask.action.payloads import (
    action_session_dictionary, set_action_payload,
)
from ontask.core.celery import celery_is_up
from ontask.core.decorators import ajax_required, get_workflow
from ontask.core.permissions import is_instructor
from ontask.core.tables import OperationsColumn
from ontask.models import Action, Log, ScheduledOperation, Workflow
from ontask.scheduler.views.save import (
    create_timedelta_string, save_canvas_email_schedule, save_email_schedule,
    save_json_schedule, save_send_list_json_schedule, save_send_list_schedule,
)


class ScheduleActionTable(tables.Table):
    """Table to show the email actions scheduled for a workflow."""

    action = tables.LinkColumn(
        verbose_name=_('Action'),
        viewname='action:edit',
        text=lambda record: record.action.name,
        kwargs={'pk': A('action.id')},
        attrs={
            'a': {
                'class': 'spin',
                'data-toggle': 'tooltip',
                'title': _('Edit the action scheduled for execution'),
            },
        },
    )

    operations = OperationsColumn(
        verbose_name='',
        orderable=False,
        template_file='scheduler/includes/partial_scheduler_operations.html',
        template_context=lambda record: {'id': record.id},
    )

    name = tables.Column(verbose_name=_('Name'))

    execute = tables.DateTimeColumn(
        verbose_name=_('Scheduled'))

    execute_until = tables.DateTimeColumn(
        verbose_name=_('Until'))

    status = tables.Column(
        verbose_name=_('Status'),
        accessor=A('get_status_display'))

    def render_name(self, record):
        """Render name as link."""
        if record.operation_type == ScheduledOperation.ACTION_RUN:
            return format_html(
                '<a href="{0}" data-toggle="tooltip" title="{1}">{2}</a>',
                reverse('scheduler:edit_scheduled_operation', kwargs={'pk': record.id}),
                _('Edit this scheduled action execution'),
                record.name)

        return 'REVIEW ScheduleActionTable'

    def render_status(self, record):
        """Render status as a link."""
        log_item = record.last_executed_log
        if not log_item:
            return record.get_status_display()

        # At this point, the object is not pending. Produce a link
        return format_html(
            '<a class="spin" href="{0}">{1}</a>',
            reverse('logs:view', kwargs={'pk': log_item.id}),
            record.get_status_display())

    class Meta:
        """Choose model, fields and sequence in the table."""

        model = ScheduledOperation

        fields = (
            'name',
            'workflow',
            'action',
            'execute',
            'execute_until',
            'status')

        sequence = (
            'name',
            'workflow',
            'action',
            'execute',
            'execute_until',
            'status',
            'operations')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'scheduler-table'}


def _edit_scheduled_action_run(
    request: HttpRequest,
    s_item: Optional[ScheduledOperation] = None,
    action: Optional[Action] = None,
) -> HttpResponse:
    """Edit a scheduled operation (either new or existing)

    :param request: HTTP request

    :param s_item: Existing schedule item being processed

    :param schedule_type: Schedule operation type, or if empty, it is contained
    in the scheduled_item

    :param workflow: Corresponding workflow for the schedule operation type, or
    if empty, it is contained in the scheduled_item

    :param action: Corresponding action for the schedule operation type, or
    if empty, it is contained in the scheduled_item

    :return: HTTP response
    """
    if s_item:
        action = s_item.action
        exclude_values = s_item.exclude_values
    else:
        exclude_values = []

    # Get the payload from the session, and if not, use the given one
    op_payload = request.session.get(action_session_dictionary)
    if not op_payload:
        op_payload = {
            'action_id': action.id,
            'prev_url': reverse(
                'scheduler:create_action_run',
                kwargs={'pk': action.id}),
            'post_url': reverse(
                'scheduler:finish_scheduling'),
            'exclude_values': exclude_values}
        if s_item:
            op_payload.update(s_item.payload)
        set_action_payload(request.session, op_payload)
        request.session.save()

    if s_item:
        op_payload['schedule_id'] = s_item.id

    if action.action_type == Action.PERSONALIZED_TEXT:
        return save_email_schedule(request, action, s_item, op_payload)
    elif action.action_type == Action.SEND_LIST:
        return save_send_list_schedule(request, action, s_item, op_payload)
    elif action.action_type == Action.SEND_LIST_JSON:
        return save_send_list_json_schedule(
            request,
            action,
            s_item,
            op_payload)
    elif action.action_type == Action.PERSONALIZED_CANVAS_EMAIL:
        return save_canvas_email_schedule(
            request,
            action,
            s_item,
            op_payload)
    elif action.action_type == Action.PERSONALIZED_JSON:
        return save_json_schedule(request, action, s_item, op_payload)

    # Action type not found, so return to the main table view
    messages.error(
        request,
        _('This action does not support scheduling'))
    return redirect('scheduler:index')


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def index(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Render the list of actions attached to a workflow.

    :param request: Request object
    :return: HTTP response with the table.
    """
    # Reset object to carry action info throughout dialogs
    set_action_payload(request.session)
    request.session.save()

    # Get the actions
    s_items = ScheduledOperation.objects.filter(action__workflow=workflow.id)

    return render(
        request,
        'scheduler/index.html',
        {
            'table': ScheduleActionTable(s_items, orderable=False),
            'workflow': workflow,
        },
    )


@user_passes_test(is_instructor)
@ajax_required
@get_workflow()
def view(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """View an existing scheduled action.

    :param request: HTTP request

    :param pk: primary key of the scheduled action

    :return: HTTP response
    """
    # Get the scheduled action
    sch_obj = ScheduledOperation.objects.filter(
        action__workflow=workflow,
        pk=pk).first()

    if not sch_obj:
        # Connection object not found, go to table of sql connections
        return JsonResponse({'html_redirect': reverse('scheduler:index')})

    # Get the values and remove the ones that are not needed
    item_values = model_to_dict(sch_obj)
    item_values['item_column'] = str(sch_obj.item_column)
    item_values['action'] = str(sch_obj.action)
    item_values.pop('id')
    item_values.pop('user')
    item_values['payload'] = json.dumps(item_values['payload'], indent=2)

    is_executing, tdelta = create_timedelta_string(
        sch_obj.execute,
        sch_obj.execute_until)
    return JsonResponse({
        'html_form': render_to_string(
            'scheduler/includes/partial_show_schedule_action.html',
            {
                's_vals': item_values,
                'id': sch_obj.id,
                'is_executing': is_executing,
                'timedelta': tdelta,
            },
        ),
    })


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def create_action_run(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Edit an existing scheduled email action.

    :param request: HTTP request

    :param pk: primary key of the action

    :return: HTTP response
    """
    action = workflow.actions.filter(pk=pk).filter(
        Q(workflow__user=request.user)
        | Q(workflow__shared=request.user),
    ).first()
    if not action:
        return redirect('home')

    return _edit_scheduled_action_run(request, None, action)


# @user_passes_test(is_instructor)
# @get_workflow(pf_related='actions')
# def create_workflow_op(
#     request: HttpRequest,
#     workflow: Optional[Workflow] = None,
# ) -> HttpResponse:
#     messages.error(
#         request,
#         _('Under implementation'))
#     return redirect('scheduler:index')
#
#
@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def edit_scheduled_operation(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Edit an existing scheduled email action.

    :param request: HTTP request

    :param pk: primary key of the action

    :return: HTTP response
    """
    s_item = ScheduledOperation.objects.filter(pk=pk).first()
    if not s_item:
        return redirect('home')

    if s_item.action:
        return _edit_scheduled_action_run(request, s_item)

    # Workflow operation
    # Action type not found, so return to the main table view
    messages.error(
        request,
        _('Under implementation'))
    return redirect('scheduler:index')

@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related='actions')
def delete(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """View screen to confirm deletion scheduled item.

    :param request: Request object

    :param pk: Scheduled item id to delete

    :return:
    """
    # Get the appropriate scheduled action
    s_item = ScheduledOperation.objects.filter(
        action__workflow=workflow,
        pk=pk,
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

    log_type = None
    if s_item.action.action_type == Action.PERSONALIZED_TEXT:
        log_type = Log.SCHEDULE_EMAIL_DELETE
    elif s_item.action.action_type == Action.SEND_LIST:
        log_type = Log.SCHEDULE_SEND_LIST_DELETE
    elif s_item.action.action_type == Action.PERSONALIZED_JSON:
        log_type = Log.SCHEDULE_JSON_DELETE
    elif s_item.action.action_type == Action.SEND_LIST_JSON:
        log_type = Log.SCHEDULE_JSON_LIST_DELETE
    elif s_item.action.action_type == Action.PERSONALIZED_CANVAS_EMAIL:
        log_type = Log.SCHEDULE_CANVAS_EMAIL_DELETE
    s_item.log(log_type)
    s_item.delete()
    return JsonResponse({'html_redirect': reverse('scheduler:index')})
