# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import django_tables2 as tables
import pytz
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django_tables2 import A
from django.utils.translation import ugettext_lazy as _

# Create your views here.
import logs
from action.models import Action
from forms import EmailForm
from ontask.permissions import is_instructor
from ontask.tables import OperationsColumn, BooleanColumn
from scheduler.models import ScheduledEmailAction
from workflow.ops import get_workflow


class ScheduleEmailActionTable(tables.Table):
    """
    Table to show the email actions scheduled for a workflow
    """

    operations = OperationsColumn(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=_('Operations'),
        orderable=False,
        template_file='scheduler/includes/partial_scheduler_operations.html',
        template_context=lambda record: {'id': record.id}
    )

    action = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Action'),
        accessor=A('action.name')
    )

    execute = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Scheduled')
    )

    status = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Status')
    )

    subject = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Subject')
    )

    email_column = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Email column'),
    )

    cc_email = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('CC Emails'),
    )

    bcc_email = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('BCC Emails'),
    )

    send_confirmation = BooleanColumn(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Send confirmation'),
        get_field=lambda x: x.send_confirmation,
    )

    track_read = BooleanColumn(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Track'),
        get_field=lambda x: x.track_read,
    )

    message = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Execution message'),
    )

    def render_action(self, record):
        return format_html(
            '<a href="{0}">{1}</a>'.format(
                reverse('action:edit_out',
                        kwargs={'pk': record.action.id}),
                record.action.name
            )
        )

    class Meta:
        model = ScheduledEmailAction

        fields = ('action', 'created', 'execute', 'status', 'subject',
                  'email_column', 'cc_email', 'bcc_email', 'send_confirmation',
                  'track_read', 'operations', 'message')

        sequence = ('operations',
                    'action',
                    'created',
                    'execute',
                    'status',
                    'subject',
                    'email_column',
                    'cc_email',
                    'bcc_email',
                    'send_confirmation',
                    'track_read',
                    'message')

        attrs = {
            'class': 'table display table-bordered',
            'id': 'scheduler-table'
        }

        row_attrs = {
            'style': 'text-align:center;',
            'class': lambda record: 'success' if record.status == 0 else ''
        }


def save_email_schedule(request, workflow, action, schedule_item):
    """
    Function to handle the creation and edition of email items
    :param request: Http request being processed
    :param workflow: workflow item related to the action
    :param action: Action item related to the schedule
    :param schedule_item: Schedule item or None if it is new
    :return:
    """

    # Create the form to ask for the email subject and other information
    form = EmailForm(data=request.POST or None,
                     instance=schedule_item,
                     columns=workflow.columns.filter(is_key=True))

    now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    # Check if the request is GET, or POST but not valid
    if request.method == 'GET' or not form.is_valid():
        # Render the form
        return render(request,
                      'scheduler/email.html',
                      {'action': action,
                       'form': form,
                       'now': now})

    # We are processing a valid POST request

    # Check that the email column has correct values (FIX)
    # correct_emails = all([validate_email(x[col_idx]) for x in data_table])

    # Save the schedule item object
    s_item = form.save(commit=False)

    # Assign additional fields and save
    s_item.user = request.user
    s_item.action = action
    s_item.type = 'email_send'
    s_item.status = 0  # Pending
    s_item.save()

    # Create the payload to record the event in the log
    payload = {
        'workflow': workflow.name,
        'workflow_id': workflow.id,
        'action': action.name,
        'action_id': action.id,
        'execute': s_item.execute.isoformat(),
        'subject': s_item.subject,
        'email_column': s_item.email_column.name,
        'send_confirmation': s_item.send_confirmation,
        'track_read': s_item.track_read
    }

    # Log the operation
    if schedule_item:
        log_type = 'schedule_email_edit'
    else:
        log_type = 'schedule_email_create'
    logs.ops.put(request.user,
                 log_type,
                 workflow,
                 payload)

    # Notify the user. Show the time left until execution and a link to
    # view the scheduled events with possibility of editing/deleting.
    # Successful processing.
    now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    tdelta = s_item.execute - now
    return render(request,
                  'scheduler/email_done.html',
                  {'tdelta': str(tdelta),
                   's_item': s_item})


@user_passes_test(is_instructor)
def index(request):
    """
    Render the list of actions attached to a workflow.
    :param request: Request object
    :return: HTTP response with the table.
    """

    # Get the appropriate workflow object
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Get the actions
    s_items = ScheduledEmailAction.objects.filter(
        action__workflow=workflow.id,
        deleted=False
    )

    return render(
        request,
        'scheduler/index.html',
        {'table': ScheduleEmailActionTable(s_items, orderable=False)}
    )


@user_passes_test(is_instructor)
def email_create(request, pk):
    """
    Request data to send emails. Form asking for subject line, email column,
    etc.
    :param request: HTTP request (GET)
    :param pk: Action key
    :return:
    """

    # Get the action attached to this request
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)).distinct().get(pk=pk)
    except ObjectDoesNotExist:
        return redirect('workflow:index')

    workflow = get_workflow(request, action.workflow.id)
    if not workflow:
        return redirect('workflow:index')

    # See if this action already has a scheduled action
    schedule_item = None
    qs = ScheduledEmailAction.objects.filter(
        action=action,
        type='email_send',
        status=0,  # Pending
        deleted=False
    )
    if qs:
        if settings.DEBUG:
            assert len(qs) == 1  # There should only be one
        schedule_item = qs[0]

    return save_email_schedule(request, workflow, action, schedule_item)


@user_passes_test(is_instructor)
def edit_email(request, pk):
    """
    Edit an existing scheduled email action
    :param request: HTTP request
    :param pk: primary key of the email action
    :return: HTTP response
    """

    # Get first the current workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Get the scheduled action from the parameter in the URL
    try:
        s_item = ScheduledEmailAction.objects.filter(
            action__workflow=workflow,
            type='email_send',
            deleted=False,
        ).get(pk=pk)
    except ObjectDoesNotExist:
        return redirect('workflow:index')

    # Get the action field.
    action = s_item.action

    return save_email_schedule(request, workflow, action, s_item)


@user_passes_test(is_instructor)
def delete_email(request, pk):
    """
    View to handle the AJAX form to delete a scheduled item.
    :param request: Request object
    :param pk: Scheduled item id to delete
    :return:
    """

    # JSON response object
    data = dict()

    # Get the appropriate scheduled action
    try:
        s_item = ScheduledEmailAction.objects.filter(
            action__workflow__user=request.user,
            deleted=False,
        ).distinct().get(pk=pk)
    except (KeyError, ObjectDoesNotExist):
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('scheduler:index')
        return JsonResponse(data)

    if request.method == 'POST':
        # Log the event
        logs.ops.put(request.user,
                     'schedule_email_delete',
                     s_item.action.workflow,
                     {'action': s_item.action.name,
                      'action_id': s_item.action.id,
                      'execute': s_item.execute.isoformat(),
                      'subject': s_item.subject,
                      'email_column': s_item.email_column.name,
                      'send_confirmation': s_item.send_confirmation,
                      'track_read': s_item.track_read})

        # Perform the delete operation
        s_item.deleted = True
        s_item.save()

        # In this case, the form is valid anyway
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('scheduler:index')

        return JsonResponse(data)

    data['html_form'] = render_to_string(
        'scheduler/includes/partial_scheduler_delete.html',
        {'s_item': s_item},
        request=request)
    return JsonResponse(data)
