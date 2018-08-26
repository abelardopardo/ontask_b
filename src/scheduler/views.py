# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import django_tables2 as tables
import pytz
from celery.task.control import inspect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.utils.html import format_html, escape
from django.utils.translation import ugettext_lazy as _, ugettext
from django_tables2 import A

from action.models import Action
from action.views_out import session_dictionary_name
from forms import EmailScheduleForm
from logs.models import Log
from ontask.permissions import is_instructor
from ontask.tables import OperationsColumn
from scheduler.models import ScheduledAction
from workflow.ops import get_workflow


class ScheduleActionTable(tables.Table):
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

    type = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Type'),
        accessor=A('get_type_display')
    )

    action = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Action'),
        accessor=A('action.name')
    )

    created = tables.DateTimeColumn(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Scheduled')
    )

    execute = tables.DateTimeColumn(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Scheduled')
    )

    status = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Status'),
        accessor=A('get_status_display')
    )

    item_column = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Item column'),
    )

    exclude_values = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Exclude'),
    )

    payload = tables.Column(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Parameters'),
    )

    last_executed_log = tables.DateTimeColumn(
        attrs={'td': {'class': 'dt-center'}},
        verbose_name=_('Result'),
    )

    def render_action(self, record):
        return format_html(
            '<a href="{0}">{1}</a>'.format(
                reverse('action:edit',
                        kwargs={'pk': record.action.id}),
                record.action.name
            )
        )

    def render_exclude_values(self, record):
        return ', '.join(record.exclude_values)

    def render_payload(self, record):
        result = ''
        if not record.payload:
            return result

        for k, v in sorted(record.payload.items()):
            if isinstance(v, list):
                result += '<li>{0}: {1}</li>'.format(
                    escape(str(k)), escape(', '.join([str(x) for x in v]))
                )
            else:
                result += '<li>{0}: {1}</li>'.format(
                    escape(str(k)), escape(str(v))
                )
        return format_html(
            '<ul style="text-align:left;">{0}<ul>'.format(result)
        )

    def render_last_executed_log(self, record):
        log_item = record.last_executed_log
        if not log_item:
            return "---"
        return format_html(
            """<a href="{0}">{1}</a>""".format(
                reverse('logs:view', kwargs={'pk': log_item.id}),
                log_item.modified.astimezone(
                    pytz.timezone(settings.TIME_ZONE)
                )
            )
        )

    class Meta:
        model = ScheduledAction

        fields = ('type', 'action', 'created', 'execute', 'status',
                  'item_column', 'exclude_values', 'operations',
                  'last_executed_log')

        sequence = ('operations',
                    'type',
                    'action',
                    'created',
                    'execute',
                    'status',
                    'item_column',
                    'exclude_values',
                    'last_executed_log')

        attrs = {
            'class': 'table display table-bordered',
            'id': 'scheduler-table'
        }

        row_attrs = {
            'style': 'text-align:center;',
            'class': lambda record: 'success' \
                if record.status == ScheduledAction.STATUS_PENDING else ''
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

    # Get the payload from the session, and if not, use the given one
    op_payload = request.session.get(session_dictionary_name, None)
    if not op_payload:
        op_payload = {'action_id': action.id,
                      'prev_url': reverse('scheduler:create_email',
                                          kwargs={'pk': action.id}),
                      'post_url': reverse('scheduler:finish_schedule')}
        request.session[session_dictionary_name] = op_payload
        request.session.save()

    # Verify that celery is running!
    celery_stats = None
    try:
        celery_stats = inspect().stats()
    except Exception as e:
        pass
    # If the stats are empty, celery is not running.
    if not celery_stats:
        messages.error(
            request,
            _('Unable to send emails due to a misconfiguration. '
              'Ask your system administrator to enable email queueing.'))
        return redirect(reverse('action:index'))

    # Create the form to ask for the email subject and other information
    form = EmailScheduleForm(
        data=request.POST or None,
        action=action,
        instance=schedule_item,
        columns=workflow.columns.filter(is_key=True),
        confirm_emails=op_payload.get('confirm_emails', False))

    now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    # Check if the request is GET, or POST but not valid
    if request.method == 'GET' or not form.is_valid():
        # Render the form
        return render(request,
                      'scheduler/email.html',
                      {'action': action,
                       'form': form,
                       'now': now})

    # Processing a valid POST request

    # Save the schedule item object
    s_item = form.save(commit=False)

    # Assign additional fields and save
    s_item.user = request.user
    s_item.action = action
    s_item.type = ScheduledAction.TYPE_EMAIL_SEND
    s_item.status = ScheduledAction.STATUS_CREATING
    s_item.payload = {
        'subject': form.cleaned_data['subject'],
        'cc_email': [x for x in form.cleaned_data['cc_email'].split(',') if x],
        'bcc_email': [x
                      for x in form.cleaned_data['bcc_email'].split(',') if x],
        'send_confirmation': form.cleaned_data['send_confirmation'],
        'track_read': form.cleaned_data['track_read']
    }
    s_item.save()

    # Upload information to the op_payload
    op_payload['schedule_id'] = s_item.id
    op_payload['exclude_values'] = s_item.exclude_values
    op_payload['confirm_emails'] = form.cleaned_data['confirm_emails']

    if op_payload['confirm_emails']:
        # Create a dictionary in the session to carry over all the
        # information to execute the next steps
        op_payload['item_column'] = s_item.item_column.name
        op_payload['button_label'] = ugettext('Schedule')
        request.session[session_dictionary_name] = op_payload

        return redirect('action:item_filter')

    # Go straight to the final step
    return scheduler_finalize_action(request, op_payload)


def scheduler_finalize_action(request, payload=None):
    """
    Finalize the creation of a scheduled action. All required data is passed
    through the payload.

    :param request: Request object received
    :param payload: Dictionary with all the required data coming from
    previous requests.
    :return:
    """

    # Get the payload from the session if not given
    if payload is None:
        payload = request.session.get(session_dictionary_name)

        # If there is no payload, something went wrong.
        if payload is None:
            # Something is wrong with this execution. Return to action table.
            messages.error(request,
                           _('Incorrect action scheduling invocation.'))
            return redirect('action:index')

    # Get the index
    s_item_id = payload.get('schedule_id')
    if not s_item_id:
        messages.error(request, _('Incorrect parameters in action scheduling'))
        return redirect('action:index')

    # Get the item being processed
    schedule_item = ScheduledAction.objects.get(pk=s_item_id)

    # Check for exclude values and store them if needed
    exclude_values = payload.get('exclude_values')
    if exclude_values:
        schedule_item.exclude_values = exclude_values

    schedule_item.status = ScheduledAction.STATUS_PENDING
    schedule_item.save()

    # Create the payload to record the event in the log
    log_payload = {
        'action': schedule_item.action.name,
        'action_id': schedule_item.action.id,
        'execute': schedule_item.execute.isoformat(),
        'email_column': schedule_item.item_column.name,
        'subject': schedule_item.payload.get('subject'),
        'cc_email': schedule_item.payload.get('cc_email', []),
        'bcc_email': schedule_item.payload.get('bcc_email', []),
        'send_confirmation': schedule_item.payload.get('send_confirmation',
                                                False),
        'track_read': schedule_item.payload.get('track_read', False)
    }

    # Log the operation
    if schedule_item:
        log_type = Log.SCHEDULE_EMAIL_EDIT
    else:
        log_type = Log.SCHEDULE_EMAIL_CREATE

    Log.objects.register(request.user,
                         log_type,
                         schedule_item.action.workflow,
                         log_payload)

    # Notify the user. Show the time left until execution and a link to
    # view the scheduled events with possibility of editing/deleting.
    # Successful processing.
    now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    tdelta = schedule_item.execute - now

    # Reset object to carry action info throughout dialogs
    request.session[session_dictionary_name] = {}
    request.session.save()

    # Successful processing.
    return render(request,
                  'scheduler/schedule_done.html',
                  {'tdelta': str(tdelta),
                   's_item': schedule_item})


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
    s_items = ScheduledAction.objects.filter(action__workflow=workflow.id,
                                             deleted=False)

    return render(request,
                  'scheduler/index.html',
                  {'table': ScheduleActionTable(s_items, orderable=False)})


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
    qs = ScheduledAction.objects.filter(
        action=action,
        type=ScheduledAction.TYPE_EMAIL_SEND,
        status=ScheduledAction.STATUS_CREATING,
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
        s_item = ScheduledAction.objects.filter(
            action__workflow=workflow,
            type=ScheduledAction.TYPE_EMAIL_SEND,
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
        s_item = ScheduledAction.objects.filter(
            action__workflow__user=request.user,
            deleted=False,
        ).distinct().get(pk=pk)
    except (KeyError, ObjectDoesNotExist):
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('scheduler:index')
        return JsonResponse(data)

    if request.method == 'POST':
        # Log the event
        Log.objects.register(
            request.user,
            Log.SCHEDULE_EMAIL_DELETE,
            s_item.action.workflow,
            {'action': s_item.action.name,
             'action_id': s_item.action.id,
             'execute': s_item.execute.isoformat(),
             'email_column': s_item.item_column.name,
             'subject': s_item.payload.get('subject'),
             'cc_email': s_item.payload.get('cc_email', []),
             'bcc_email': s_item.payload.get('bcc_email', []),
             'send_confirmation': s_item.payload.get('send_confirmation',
                                                     False),
             'track_read': s_item.payload.get('track_read', False)}
        )

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
