# -*- coding: utf-8 -*-


import json

from celery.task.control import inspect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _, ugettext
from django.views.decorators.csrf import csrf_exempt

from action.evaluate import (
    get_row_values,
    evaluate_row_action_out,
    evaluate_row_action_in)
from action.models import Action
from logs.models import Log
from ontask.permissions import is_instructor
from ontask.tasks import send_email_messages, send_json_objects
from workflow.ops import get_workflow
from .forms import EmailActionForm, JSONActionForm, EmailExcludeForm

# Dictionary to store in the session the data between forms.
session_dictionary_name = 'action_run_payload'


def run_email_action(request, workflow, action):
    """
    Request data to send emails. Form asking for subject line, email column,
    etc.
    :param request: HTTP request (GET)
    :param workflow: Workflow object
    :param action: Action object
    :return: HTTP response
    """

    # Get the payload from the session, and if not, use the given one
    op_payload = request.session.get(session_dictionary_name, None)
    if not op_payload:
        op_payload = {'action_id': action.id,
                      'prev_url': reverse('action:run',
                                          kwargs={'pk': action.id}),
                      'post_url': reverse('action:email_done')}
        request.session[session_dictionary_name] = op_payload
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
            _('Unable to send emails due to a misconfiguration. '
              'Ask your system administrator to enable email queueing.'))
        return redirect(reverse('action:index'))

    # Create the form to ask for the email subject and other information
    form = EmailActionForm(
        request.POST or None,
        column_names=[x.name for x in workflow.columns.filter(is_key=True)],
        action=action,
        op_payload=op_payload
    )

    # Process the GET or invalid
    if request.method == 'GET' or not form.is_valid():
        # Get the number of rows from the action
        filter_obj = action.get_filter()
        num_msgs = filter_obj.n_rows_selected if filter_obj else -1
        if num_msgs == -1:
            # There is no filter in the action, so take the number of rows
            num_msgs = workflow.nrows

        # Render the form
        return render(request,
                      'action/action_email_step1.html',
                      {'action': action,
                       'num_msgs': num_msgs,
                       'form': form})

    # Requet is a POST and is valid

    # Collect information from the form and store it in op_payload
    op_payload['subject'] = form.cleaned_data['subject']
    op_payload['item_column'] = form.cleaned_data['email_column']
    op_payload['cc_email'] = form.cleaned_data['cc_email']
    op_payload['bcc_email'] = form.cleaned_data['bcc_email']
    op_payload['confirm_emails'] = form.cleaned_data['confirm_emails']
    op_payload['send_confirmation'] = form.cleaned_data['send_confirmation']
    op_payload['track_read'] = form.cleaned_data['track_read']
    op_payload['export_wf'] = form.cleaned_data['export_wf']
    op_payload['exclude_values'] = []

    if op_payload['confirm_emails']:
        # Create a dictionary in the session to carry over all the information
        # to execute the next pages
        op_payload['button_label'] = ugettext('Send')
        request.session[session_dictionary_name] = op_payload

        return redirect('action:item_filter')

    # Go straight to the final step.
    return run_email_action_done(request, op_payload)


def run_email_action_done(request, payload=None):
    """
    Final step. Create the log object, queue the operation request,
    and render the DONE page.

    :param request: HTTP request (GET)
    :param payload: Dictionary containing all the required parameters. If
    empty, the ditionary is taken from the session.
    :return: HTTP response
    """

    # Get the payload from the session if not given
    if payload is None:
        payload = request.session.get(session_dictionary_name)

        # If there is no payload, something went wrong.
        if payload is None:
            # Something is wrong with this execution. Return to action table.
            messages.error(request, _('Incorrect email action invocation.'))
            return redirect('action:index')

    # Get the information from the payload
    action = Action.objects.get(pk=payload['action_id'])
    subject = payload['subject']
    email_column = payload['item_column']
    cc_email = [x.strip() for x in payload['cc_email'].split(',') if x]
    bcc_email = [x.strip() for x in payload['bcc_email'].split(',') if x]
    send_confirmation = payload['send_confirmation']
    track_read = payload['track_read']
    export_wf = payload['export_wf']
    exclude_values = payload['exclude_values']

    # Log the event
    log_item = Log.objects.register(request.user,
                                    Log.SCHEDULE_EMAIL_EXECUTE,
                                    action.workflow,
                                    {'action': action.name,
                                     'action_id': action.id,
                                     'bcc_email': bcc_email,
                                     'cc_email': cc_email,
                                     'email_column': email_column,
                                     'exclude_values': exclude_values,
                                     'from_email': request.user.email,
                                     'send_confirmation': send_confirmation,
                                     'status': 'Preparing to execute',
                                     'subject': subject,
                                     'track_read': track_read})

    # Send the emails!
    # send_email_messages(request.user.id,
    send_email_messages.delay(request.user.id,
                              action.id,
                              subject,
                              email_column,
                              request.user.email,
                              cc_email,
                              bcc_email,
                              send_confirmation,
                              track_read,
                              exclude_values,
                              log_item.id)

    # Reset object to carry action info throughout dialogs
    request.session[session_dictionary_name] = {}
    request.session.save()

    # Successful processing.
    return render(request,
                  'action/action_done.html',
                  {'log_id': log_item.id, 'download': export_wf})


def run_json_action(request, workflow, action):
    """
    Request data to send JSON objects. Form asking for...
    :param request: HTTP request (GET)
    :param workflow: Workflow object
    :param action: Action object
    :return:
    """

    # Get the payload from the session, and if not, use the given one
    op_payload = request.session.get(session_dictionary_name, None)
    if not op_payload:
        op_payload = {'action_id': action.id,
                      'prev_url': reverse('action:run',
                                          kwargs={'pk': action.id}),
                      'post_url': reverse('action:json_done')}
        request.session[session_dictionary_name] = op_payload
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
            _('Unable to send json objects due to a misconfiguration. '
              'Ask your system administrator to enable JSON queueing.'))
        return redirect(reverse('action:index'))

    # Create the form to ask for the email subject and other information
    form = JSONActionForm(request.POST or None,
                          column_names=[x.name for x in
                                        workflow.columns.filter(is_key=True)],
                          op_payload=op_payload)

    # Process the GET or invalid
    if request.method == 'GET' or not form.is_valid():
        # Get the number of rows from the action
        filter_obj = action.get_filter()
        num_msgs = filter_obj.n_rows_selected if filter_obj else workflow.nrows

        # Render the form
        return render(request,
                      'action/request_json_data.html',
                      {'action': action,
                       'num_msgs': num_msgs,
                       'form': form})

    # Requet is a POST and is valid

    # Collect the information from the form
    op_payload['key_column'] = form.cleaned_data['key_column']
    op_payload['token'] = form.cleaned_data['token']

    if op_payload['key_column']:
        # Create a dictionary in the session to carry over all the information
        # to execute the next pages
        op_payload['item_column'] = op_payload['key_column']
        op_payload['button_label'] = ugettext('Send')
        request.session[session_dictionary_name] = op_payload

        return redirect('action:item_filter')

    # Go straight to the final step.
    return json_done(request, op_payload)


def json_done(request, payload=None):
    """
    Final step. Create the log object, queue the operation request,
    and render the DONE page.

    :param request: HTTP request (GET)
    :param payload: Dictionary containing all the required parameters. If
    empty, the ditionary is taken from the session.
    :return: HTTP response
    """

    # Get the payload from the session if not given
    if payload is None:
        payload = request.session.get(session_dictionary_name)

        # If there is no payload, something went wrong.
        if payload is None:
            # Something is wrong with this execution. Return to action table.
            messages.error(request, _('Incorrect JSON action invocation.'))
            return redirect('action:index')

    # Get the information from the payload
    action = Action.objects.get(pk=payload['action_id'])
    token = payload['token']
    key_column = payload['key_column']
    exclude_values = payload.get('exclude_values', [])

    # Log the event
    log_item = Log.objects.register(request.user,
                                    Log.SCHEDULE_JSON_EXECUTE,
                                    action.workflow,
                                    {'action': action.name,
                                     'action_id': action.id,
                                     'exclude_values': exclude_values,
                                     'key_column': key_column,
                                     'status': 'Preparing to execute',
                                     'target_url': action.target_url})

    # Send the objects
    # send_json_objects(request.user.id,
    send_json_objects.delay(request.user.id,
                            action.id,
                            token,
                            key_column,
                            exclude_values,
                            log_item.id)

    # Reset object to carry action info throughout dialogs
    request.session[session_dictionary_name] = {}
    request.session.save()

    # Successful processing.
    return render(request, 'action/action_done.html', {'log_id': log_item.id})


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
    filter_obj = action.get_filter()
    n_items = filter_obj.n_rows_selected if filter_obj else -1
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


def run_action_item_filter(request):
    """
    Offer a select widget to tick students to exclude from the email.
    :param request: HTTP request (GET)
    :return: HTTP response
    """

    # Get the payload from the session, and if not, use the given one
    payload = request.session.get(session_dictionary_name, None)
    if not payload:
        # Something is wrong with this execution. Return to the action table.
        messages.error(request, _('Incorrect item filter invocation.'))
        return redirect('action:index')

    # Get the information from the payload
    action = Action.objects.get(pk=payload['action_id'])

    form = EmailExcludeForm(request.POST or None,
                            action=action,
                            column_name=payload['item_column'],
                            exclude_values=payload.get('exclude_values', list))
    context = {
        'form': form,
        'action': action,
        'button_label': payload['button_label'],
        'prev_step': payload['prev_url']
    }

    # Process the initial loading of the form and return
    if request.method != 'POST' or not form.is_valid():
        return render(request, 'action/item_filter.html', context)

    # Updating the content of the exclude_values in the payload
    payload['exclude_values'] = form.cleaned_data['exclude_values']

    return redirect(payload['post_url'])
