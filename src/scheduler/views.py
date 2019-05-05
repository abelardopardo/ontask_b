# -*- coding: utf-8 -*-


import datetime
import json
from builtins import object
from typing import Optional

import django_tables2 as tables
import pytz
from celery.task.control import inspect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _, ugettext
from django_tables2 import A
from past.utils import old_div

from action.models import Action
from action.payloads import action_session_dictionary
from logs.models import Log
from ontask.decorators import get_workflow, check_workflow
from ontask.permissions import is_instructor
from ontask.tables import OperationsColumn
from scheduler.models import ScheduledAction
from workflow.models import Workflow
from .forms import EmailScheduleForm, JSONScheduleForm, CanvasEmailScheduleForm


class ScheduleActionTable(tables.Table):
    """
    Table to show the email actions scheduled for a workflow
    """

    operations = OperationsColumn(
        verbose_name='',
        orderable=False,
        template_file='scheduler/includes/partial_scheduler_operations.html',
        template_context=lambda record: {'id': record.id}
    )

    name = tables.Column(verbose_name=_('Name'))

    action = tables.Column(
        verbose_name=_('Action'),
        accessor=A('action.name')
    )

    execute = tables.DateTimeColumn(
        verbose_name=_('Scheduled')
    )

    status = tables.Column(
        verbose_name=_('Status'),
        accessor=A('get_status_display')
    )

    def render_name(self, record):
        return format_html(
            """<a href="{0}"
                  data-toggle="tooltip"
                  title="{1}">{2}</a>""",
            reverse('scheduler:edit', kwargs={'pk': record.id}),
            _('Edit this scheduled action execution'),
            record.name
        )

    def render_action(self, record):
        icon = 'file-text'
        if record.action.action_type == Action.personalized_text:
            icon = 'file-text'
            title = 'Personalized text'
        elif record.action.action_type == Action.personalized_canvas_email:
            icon = 'envelope-square'
            title = 'Personalized Canvas Email'
        elif record.action.action_type == Action.personalized_json:
            icon = 'code'
            title = 'Personalized JSON'
        elif record.action.action_type == Action.survey:
            icon = 'question-circle-o'
            title = 'Survey'

        return format_html(
            '<a class="spin" href="{0}"'
            '   data-toggle="tooltip" title="{1}">{2}'.format(
                reverse('action:edit',
                        kwargs={'pk': record.action.id}),
                _('Edit the action scheduled for execution'),
                record.action.name,
                icon
            )
        )

    def render_status(self, record):
        log_item = record.last_executed_log
        if not log_item:
            return record.get_status_display()

        # At this point, the object is not pending. Produce a link
        return format_html(
            """<a class="spin" href="{0}">{1}</a>""",
            reverse('logs:view', kwargs={'pk': log_item.id}),
            record.get_status_display()
        )

    class Meta(object):
        model = ScheduledAction

        fields = ('name', 'action', 'execute', 'status')

        sequence = ('name', 'action', 'execute', 'status', 'operations')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'scheduler-table'
        }


def save_email_schedule(request, action, schedule_item, op_payload):
    """
    Function to handle the creation and edition of email items
    :param request: Http request being processed
    :param action: Action item related to the schedule
    :param schedule_item: Schedule item or None if it is new
    :param op_payload: dictionary to carry over the request to the next step
    :return:
    """

    # Create the form to ask for the email subject and other information
    form = EmailScheduleForm(
        data=request.POST or None,
        action=action,
        instance=schedule_item,
        columns=action.workflow.columns.filter(is_key=True),
        confirm_items=op_payload.get('confirm_items', False))

    # Check if the request is GET, or POST but not valid
    if request.method == 'GET' or not form.is_valid():
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        # Render the form
        return render(request,
                      'scheduler/edit.html',
                      {'action': action,
                       'form': form,
                       'now': now})

    # Processing a valid POST request

    # Save the schedule item object
    s_item = form.save(commit=False)

    # Assign additional fields and save
    s_item.user = request.user
    s_item.action = action
    s_item.status = ScheduledAction.STATUS_CREATING
    s_item.payload = {
        'subject': form.cleaned_data['subject'],
        'cc_email': [x for x in form.cleaned_data['cc_email'].split(',')
                     if
                     x],
        'bcc_email': [x
                      for x in form.cleaned_data['bcc_email'].split(',')
                      if
                      x],
        'send_confirmation': form.cleaned_data['send_confirmation'],
        'track_read': form.cleaned_data['track_read']
    }
    # Verify that that action does comply with the name uniqueness
    # property (only with respec to other actions)
    try:
        s_item.save()
    except IntegrityError:
        # There is an action with this name already
        form.add_error('name',
                       _('A scheduled execution of this action with this name '
                         'already exists'))
        return render(request,
                      'scheduler/edit.html',
                      {'action': action,
                       'form': form,
                       'now': datetime.datetime.now(pytz.timezone(
                           settings.TIME_ZONE))})

    # Upload information to the op_payload
    op_payload['schedule_id'] = s_item.id
    op_payload['confirm_items'] = form.cleaned_data['confirm_items']

    if op_payload['confirm_items']:
        # Update information to carry to the filtering stage
        op_payload['exclude_values'] = s_item.exclude_values
        op_payload['item_column'] = s_item.item_column.name
        op_payload['button_label'] = ugettext('Schedule')
        request.session[action_session_dictionary] = op_payload

        return redirect('action:item_filter')
    else:
        # If there is not item_column, the exclude values should be empty.
        s_item.exclude_values = []
        s_item.save()

    # Go straight to the final step
    return finish_scheduling(request, s_item, op_payload)


def save_canvas_email_schedule(request, action, schedule_item,
                               op_payload):
    """
    Function to handle the creation and edition of email items
    :param request: Http request being processed
    :param action: Action item related to the schedule
    :param schedule_item: Schedule item or None if it is new
    :param op_payload: dictionary to carry over the request to the next step
    :return:
    """

    return render(request, 'under_construction.html', {})

    # Create the form to ask for the email subject and other information
    form = CanvasEmailScheduleForm(
        data=request.POST or None,
        action=action,
        instance=schedule_item,
        columns=action.workflow.columns.filter(is_key=True),
        confirm_items=op_payload.get('confirm_items', False))

    # Check if the request is GET, or POST but not valid
    if request.method == 'GET' or not form.is_valid():
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        # Render the form
        return render(request,
                      'scheduler/edit.html',
                      {'action': action,
                       'form': form,
                       'now': now})

    # Processing a valid POST request

    # Save the schedule item object
    s_item = form.save(commit=False)

    # Assign additional fields and save
    s_item.user = request.user
    s_item.action = action
    s_item.status = ScheduledAction.STATUS_CREATING
    s_item.payload = {
        'subject': form.cleaned_data['subject'],
        'token': form.cleaned_data['token'],
    }
    # Verify that that action does comply with the name uniqueness
    # property (only with respect to other actions)
    try:
        s_item.save()
    except IntegrityError:
        # There is an action with this name already
        form.add_error('name',
                       _('A scheduled execution of this action with this name '
                         'already exists'))
        return render(request,
                      'scheduler/edit.html',
                      {'action': action,
                       'form': form,
                       'now': datetime.datetime.now(pytz.timezone(
                           settings.TIME_ZONE))})

    # Upload information to the op_payload
    op_payload['schedule_id'] = s_item.id
    op_payload['confirm_items'] = form.cleaned_data['confirm_items']

    if op_payload['confirm_items']:
        # Update information to carry to the filtering stage
        op_payload['exclude_values'] = s_item.exclude_values
        op_payload['item_column'] = s_item.item_column.name
        op_payload['button_label'] = ugettext('Schedule')
        request.session[action_session_dictionary] = op_payload

        return redirect('action:item_filter')
    else:
        # If there is not item_column, the exclude values should be empty.
        s_item.exclude_values = []
        s_item.save()

    # Go straight to the final step
    return finish_scheduling(request, s_item, op_payload)


def save_json_schedule(request, action, schedule_item, op_payload):
    """
    Function to handle the creation and edition of email items
    :param request: Http request being processed
    :param action: Action item related to the schedule
    :param schedule_item: Schedule item or None if it is new
    :param op_payload: dictionary to carry over the request to the next step
    :return:
    """

    # Create the form to ask for the email subject and other information
    form = JSONScheduleForm(
        data=request.POST or None,
        action=action,
        instance=schedule_item,
        columns=action.workflow.columns.filter(is_key=True),
        confirm_items=op_payload.get('confirm_items', False))

    # Check if the request is GET, or POST but not valid
    if request.method == 'GET' or not form.is_valid():
        now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
        # Render the form
        return render(request,
                      'scheduler/edit.html',
                      {'action': action,
                       'form': form,
                       'now': now})

    # Processing a valid POST request

    # Save the schedule item object
    s_item = form.save(commit=False)

    # Assign additional fields and save
    s_item.user = request.user
    s_item.action = action
    s_item.status = ScheduledAction.STATUS_CREATING
    s_item.payload = {
        'token': form.cleaned_data['token']
    }
    s_item.save()

    # Upload information to the op_payload
    op_payload['schedule_id'] = s_item.id

    if s_item.item_column:
        # Create a dictionary in the session to carry over all the
        # information to execute the next steps
        op_payload['item_column'] = s_item.item_column.name
        op_payload['exclude_values'] = s_item.exclude_values
        op_payload['button_label'] = ugettext('Schedule')
        request.session[action_session_dictionary] = op_payload

        return redirect('action:item_filter')
    else:
        # If there is not item_column, the exclude values should be empty.
        s_item.exclude_values = []
        s_item.save()

    # Go straight to the final step
    return finish_scheduling(request, s_item, op_payload)


def finish_scheduling(request, schedule_item=None, payload=None):
    """
    Finalize the creation of a scheduled action. All required data is passed
    through the payload.

    :param request: Request object received
    :param schedule_item: ScheduledAction item being processed. If None,
    it has to be extracted from the information in the payload.
    :param payload: Dictionary with all the required data coming from
    previous requests.
    :return:
    """

    # Get the payload from the session if not given
    if payload is None:
        payload = request.session.get(action_session_dictionary)

        # If there is no payload, something went wrong.
        if payload is None:
            # Something is wrong with this execution. Return to action table.
            messages.error(request,
                           _('Incorrect action scheduling invocation.'))
            return redirect('action:index')

    # Get the scheduled item if needed
    if not schedule_item:
        s_item_id = payload.get('schedule_id')
        if not s_item_id:
            messages.error(request,
                           _(
                               'Incorrect parameters in action scheduling'))
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
    }
    if schedule_item.action.action_type == Action.personalized_text:
        log_payload.update({
            'email_column': schedule_item.item_column.name,
            'subject': schedule_item.payload.get('subject'),
            'cc_email': schedule_item.payload.get('cc_email', []),
            'bcc_email': schedule_item.payload.get('bcc_email', []),
            'send_confirmation': schedule_item.payload.get(
                'send_confirmation',
                False),
            'track_read': schedule_item.payload.get('track_read', False)
        })
        log_type = Log.SCHEDULE_EMAIL_EDIT
    elif schedule_item.action.action_type == Action.personalized_json:
        ivalue = None
        if schedule_item.item_column:
            ivalue = schedule_item.item_column.name
        log_payload.update({
            'item_column': ivalue,
            'token': schedule_item.payload.get('subject')
        })
        log_type = Log.SCHEDULE_JSON_EDIT
    elif schedule_item.action.action_type == Action.personalized_canvas_email:
        ivalue = None
        if schedule_item.item_column:
            ivalue = schedule_item.item_column.name
        log_payload.update({
            'item_column': ivalue,
            'token': schedule_item.payload.get('subject'),
            'subject': schedule_item.payload.get('subject'),
        })
        log_type = Log.SCHEDULE_CANVAS_EMAIL_EXECUTE
    else:
        messages.error(request,
                       _('This type of actions cannot be scheduled'))
        return redirect('action:index')

    # Create the log
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
    request.session[action_session_dictionary] = None
    request.session.save()

    # Create the timedelta string
    delta_string = ''
    if tdelta.days != 0:
        delta_string += ugettext('{0} days').format(tdelta.days)
    hours = old_div(tdelta.seconds, 3600)
    if hours != 0:
        delta_string += ugettext(', {0} hours').format(hours)
    minutes = old_div((tdelta.seconds % 3600), 60)
    if minutes != 0:
        delta_string += ugettext(', {0} minutes').format(minutes)

    # Successful processing.
    return render(request,
                  'scheduler/schedule_done.html',
                  {'tdelta': delta_string,
                   's_item': schedule_item})


@user_passes_test(is_instructor)
@check_workflow(pf_related='actions')
def index(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """
    Render the list of actions attached to a workflow.
    :param request: Request object
    :return: HTTP response with the table.
    """
    # Get the actions
    s_items = ScheduledAction.objects.filter(
        action__workflow=workflow.id
    )

    return render(
        request,
        'scheduler/index.html',
        {
            'table': ScheduleActionTable(
                s_items,
                orderable=False),
            'workflow': workflow})


@user_passes_test(is_instructor)
@check_workflow()
def view(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """View an existing scheduled action.

    :param request: HTTP request

    :param pk: primary key of the scheduled action

    :return: HTTP response
    """
    # Get the scheduled action
    sch_obj = ScheduledAction.objects.filter(
        action__workflow=workflow,
        pk=pk).first()

    if not sch_obj:
        # Connection object not found, go to table of sql connections
        return JsonResponse({'html_redirect': reverse('schedule:index')})

    # Get the values and remove the ones that are not needed
    values = model_to_dict(sch_obj)
    values.pop('id')
    values.pop('user')
    values['payload'] = json.dumps(values['payload'], indent=2)

    return JsonResponse({
        'html_form': render_to_string(
            'scheduler/includes/partial_show_schedule_action.html',
            {'s_vals': values, 'id': sch_obj.id}
        )
    })


@user_passes_test(is_instructor)
@check_workflow(pf_related='actions')
def edit(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """
    Edit an existing scheduled email action
    :param request: HTTP request
    :param pk: primary key of the action
    :return: HTTP response
    """
    # Distinguish between creating a new element or editing an existing one
    new_item = request.path.endswith(reverse(
        'scheduler:create',
        kwargs={'pk': pk}))

    if new_item:
        action = workflow.actions.filter(
            pk=pk,
        ).filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)
        ).first()
        if not action:
            return redirect('home')
        s_item = None
    else:
        # Get the scheduled action from the parameter in the URL
        s_item = ScheduledAction.objects.filter(pk=pk).first()
        if not s_item:
            return redirect('home')
        action = s_item.action

    # Get the payload from the session, and if not, use the given one
    op_payload = request.session.get(action_session_dictionary, None)
    if not op_payload:
        op_payload = {'action_id': action.id,
                      'prev_url': reverse('scheduler:create',
                                          kwargs={'pk': action.id}),
                      'post_url': reverse(
                          'scheduler:finish_scheduling')}
        request.session[action_session_dictionary] = op_payload
        request.session.save()

    # Verify that celery is running!
    celery_stats = None
    try:
        celery_stats = inspect().stats()
    except Exception:
        pass
    # If the stats are empty, celery is not running.
    if not celery_stats:
        messages.error(
            request,
            _('Unable to schedule actions due to a misconfiguration. '
              'Ask your system administrator to enable queueing.'))
        return redirect(reverse('action:index'))

    if action.action_type == Action.personalized_text:
        return save_email_schedule(request, action, s_item, op_payload)
    elif action.action_type == Action.personalized_canvas_email:
        return save_canvas_email_schedule(request, action, s_item,
                                          op_payload)
    elif action.action_type == Action.personalized_json:
        return save_json_schedule(request, action, s_item, op_payload)

    # Action type not found, so return to the main table view
    messages.error(request,
                   _('This action does not support scheduling'))
    return redirect('scheduler:index')


@user_passes_test(is_instructor)
@check_workflow(pf_related='actions')
def delete(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """View screen to confirm deletion scheduled item.

    :param request: Request object

    :param pk: Scheduled item id to delete

    :return:
    """
    # Get the appropriate scheduled action
    s_item = ScheduledAction.objects.filter(
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
                request=request)
        })

    log_type = None
    if s_item.action.action_type == Action.personalized_text:
        log_type = Log.SCHEDULE_EMAIL_DELETE
    elif s_item.action.action_type == Action.personalized_json:
        log_type = Log.SCHEDULE_JSON_DELETE
    elif s_item.action.action_type == Action.personalized_canvas_email:
        log_type = Log.SCHEDULE_CANVAS_EMAIL_DELETE

    # Log the event
    if s_item.item_column:
        item_column_name = s_item.item_column.name
    else:
        item_column_name = None

    Log.objects.register(
        request.user,
        log_type,
        s_item.action.workflow,
        {'action': s_item.action.name,
         'action_id': s_item.action.id,
         'execute': s_item.execute.isoformat(),
         'item_column': item_column_name,
         'subject': s_item.payload.get('subject'),
         'cc_email': s_item.payload.get('cc_email', []),
         'bcc_email': s_item.payload.get('bcc_email', []),
         'send_confirmation': s_item.payload.get('send_confirmation',
                                                 False),
         'track_read': s_item.payload.get('track_read', False)}
    )

    # Perform the delete operation
    s_item.delete()

    return JsonResponse({'html_redirect': reverse('scheduler:index')})
