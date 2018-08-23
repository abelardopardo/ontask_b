# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import json

from celery.task.control import inspect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

import logs.ops
from action.evaluate import (
    get_row_values,
    evaluate_row_action_out,
    evaluate_row_action_in)
from action.models import Action
from ontask.permissions import is_instructor
from ontask.tasks import send_email_messages, send_json_objects
from workflow.ops import get_workflow
from .forms import EmailActionForm, JSONActionForm


def run_email_action(request, workflow, action):
    """
    Request data to send emails. Form asking for subject line, email column,
    etc.
    :param request: HTTP request (GET)
    :param workflow: Workflow object
    :param action: Action object
    :return: HTTP response
    """

    # Create the form to ask for the email subject and other information
    form = EmailActionForm(request.POST or None,
                           column_names=workflow.get_column_names(),
                           action=action)

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

    # Process the GET or invalid
    if request.method == 'GET' or not form.is_valid():
        # Get the number of rows from the action
        filter_c = action.conditions.filter(is_filter=True).first()
        num_msgs = filter_c.n_rows_selected if filter_c else -1
        if num_msgs == -1:
            # There is no filter in the action, so take the number of rows
            num_msgs = workflow.nrows

        # Render the form
        return render(request,
                      'action/request_email_data.html',
                      {'action': action,
                       'num_msgs': num_msgs,
                       'form': form})

    # Requet is a POST and is valid
    subject = form.cleaned_data['subject']
    email_column = form.cleaned_data['email_column']
    cc_email = [x.strip() for x in form.cleaned_data['cc_email'].split(',')
                if x]
    bcc_email = [x.strip() for x in form.cleaned_data['bcc_email'].split(',')
                 if x]
    send_confirmation = form.cleaned_data['send_confirmation']
    track_read = form.cleaned_data['track_read']

    # Log the event
    log_item = logs.ops.put(request.user,
                            'schedule_email_execute',
                            action.workflow,
                            {'action': action.name,
                             'action_id': action.id,
                             'from_email': request.user.email,
                             'subject': subject,
                             'email_column': email_column,
                             'cc_email': cc_email,
                             'bcc_email': bcc_email,
                             'send_confirmation': send_confirmation,
                             'track_read': track_read,
                             'status': 'Preparing to execute'})

    # Send the emails!
    # send_email_messages(request.user.id,
    send_email_messages.delay(request.user.id,
                              action.id,
                              form.cleaned_data['subject'],
                              form.cleaned_data['email_column'],
                              request.user.email,
                              cc_email,
                              bcc_email,
                              send_confirmation,
                              track_read,
                              log_item.id)

    # If the export has been requested, go there and send it as
    # response
    context = {'log_id': log_item.id}
    if form.cleaned_data['export_wf']:
        context['download'] = True

    # Successful processing.
    return render(request,
                  'action/action_done.html',
                  context)


def run_json_action(request, workflow, action):
    """
    Request data to send JSON objects. Form asking for...
    :param request: HTTP request (GET)
    :param workflow: Workflow object
    :param action: Action object
    :return:
    """

    # Create the form to ask for the email subject and other information
    form = JSONActionForm(request.POST or None)

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
            _('Unable to send json objects due to a misconfiguration. '
              'Ask your system administrator to enable json queueing.'))
        return redirect(reverse('action:index'))

    # Process the GET or invalid
    if request.method == 'GET' or not form.is_valid():
        # Get the number of rows from the action
        filter_c = action.conditions.filter(is_filter=True).first()
        num_msgs = filter_c.n_rows_selected if filter_c else -1
        if num_msgs == -1:
            # There is no filter in the action, so take the number of rows
            num_msgs = workflow.nrows

        # Render the form
        return render(request,
                      'action/request_json_data.html',
                      {'action': action,
                       'num_msgs': num_msgs,
                       'form': form})

    # Requet is a POST and is valid

    # Log the event
    log_item = logs.ops.put(request.user,
                            'schedule_json_execute',
                            action.workflow,
                            {'action': action.name,
                             'action_id': action.id,
                             'target_url': action.target_url,
                             'status': 'Preparing to execute'})

    # Send the objects
    send_json_objects(request.user.id,
    # send_json_objects.delay(request.user.id,
                            action.id,
                            form.cleaned_data['token'],
                            log_item.id)

    context = {'log_id': log_item.id, 'action': action}

    # Successful processing.
    return render(request,
                  'action/action_done.html',
                  context)


@csrf_exempt
@user_passes_test(is_instructor)
def preview_response(request, pk, idx):
    """
    HTML request and the primary key of an action to preview one of its
    instances. The request must provide and additional parameter idx to
    denote which instance to show.

    :param request: HTML request object
    :param pk: Primary key of the an action for which to do the preview
    :param idx: Index of the reponse to preview
    :param template: Path to the template to use for the render.
    :param prelude: Optional text to include at the top of the rencering
    :return:
    """

    # To include in the JSON response
    data = dict()

    # Action being used
    try:
        action = Action.objects.get(id=pk)
    except ObjectDoesNotExist:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    # Get the workflow to obtain row numbers
    workflow = get_workflow(request, action.workflow.id)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content', None)
    if action_content:
        action.set_content(action_content)
        action.save()

    # Turn the parameter into an integer
    idx = int(idx)

    # Get the total number of items
    cfilter = action.conditions.filter(is_filter=True).first()
    n_items = cfilter.n_rows_selected if cfilter else -1
    if n_items == -1:
        n_items = workflow.nrows

    # Set the idx to a legal value just in case
    if not 1 <= idx <= n_items:
        idx = 1

    prv = idx - 1
    if prv <= 0:
        prv = n_items

    nxt = idx + 1
    if nxt > n_items:
        nxt = 1

    row_values = get_row_values(action, idx)

    # Get the dictionary containing column names, attributes and condition
    # valuations:
    context = action.get_evaluation_context(row_values)

    # Evaluate the action content.
    show_values = ''
    correct_json = True
    if action.is_out:
        action_content = evaluate_row_action_out(action, context)
        if action.action_type == Action.PERSONALIZED_JSON:
            try:
                __ = json.loads(action_content)
            except Exception:
                correct_json = False
    else:
        action_content = evaluate_row_action_in(action, context)
    if action_content:
        # Get the conditions used in the action content
        act_cond = action.get_action_conditions()
        # Get the variables/columns from the conditions
        act_vars = set().union(
            *[x.columns.all()
              for x in action.conditions.filter(name__in=act_cond)
              ]
        )
        # Sort the variables/columns  by position and get the name
        show_values = ', '.join(
            ["{0} = {1}".format(x.name, row_values[x.name]) for x in act_vars]
        )
    else:
        action_content = \
            _("Error while retrieving content for student {0}").format(idx)

    # See if there is prelude content in the request
    prelude = request.GET.get('subject_content', None)
    if prelude:
        prelude = evaluate_row_action_out(action, context, prelude)

    data['html_form'] = \
        render_to_string('action/includes/partial_preview.html',
                         {'action': action,
                          'action_content': action_content,
                          'index': idx,
                          'n_items': n_items,
                          'nxt': nxt,
                          'prv': prv,
                          'prelude': prelude,
                          'correct_json': correct_json,
                          'show_values': show_values},
                         request=request)

    return JsonResponse(data)
