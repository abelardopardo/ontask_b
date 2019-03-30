# -*- coding: utf-8 -*-


import json
import zipfile
from datetime import datetime, timedelta
from io import BytesIO

import pytz
from celery.task.control import inspect
from django.conf import settings as ontask_settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _, ugettext
from django.views.decorators.csrf import csrf_exempt

from action.evaluate import (
    get_row_values,
    evaluate_row_action_out,
    evaluate_row_action_in, evaluate_action
)
from action.models import Action
from action.ops import get_workflow_action
from dataops.pandas_db import get_table_cursor
from logs.models import Log
from ontask import action_session_dictionary, get_action_payload
from ontask.permissions import is_instructor
from ontask.tasks import (
    send_email_messages, send_json_objects,
    send_canvas_email_messages
)
from ontask_oauth.models import OnTaskOAuthUserTokens
from ontask_oauth.views import get_initial_token_step1, refresh_token
from workflow.ops import get_workflow
from .forms import (
    EmailActionForm, JSONActionForm, ZipActionForm, CanvasEmailActionForm
)

html_body = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>title</title>
  </head>
  <body>
    {0}
  </body>
</html>"""


def run_email_action(request, workflow, action):
    """
    Request data to send emails. Form asking for subject line, email column,
    etc.
    :param request: HTTP request (GET)
    :param workflow: workflow being processed
    :param action: Action begin run
    :return: HTTP response
    """

    # Get the payload from the session, and if not, use the given one
    op_payload = get_action_payload(request)
    if not op_payload:
        op_payload = {'action_id': action.id,
                      'prev_url': reverse('action:run',
                                          kwargs={'pk': action.id}),
                      'post_url': reverse('action:email_done')}
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
                      'action/request_email_data.html',
                      {'action': action,
                       'num_msgs': num_msgs,
                       'form': form,
                       'valuerange': range(2),
                       'rows_all_false': action.get_row_all_false_count()})

    # Request is a POST and is valid

    # Collect information from the form and store it in op_payload
    op_payload['subject'] = form.cleaned_data['subject']
    op_payload['item_column'] = form.cleaned_data['email_column']
    op_payload['cc_email'] = form.cleaned_data['cc_email']
    op_payload['bcc_email'] = form.cleaned_data['bcc_email']
    op_payload['confirm_items'] = form.cleaned_data['confirm_items']
    op_payload['send_confirmation'] = form.cleaned_data['send_confirmation']
    op_payload['track_read'] = form.cleaned_data['track_read']
    op_payload['export_wf'] = form.cleaned_data['export_wf']
    op_payload['exclude_values'] = []

    if op_payload['confirm_items']:
        # Create a dictionary in the session to carry over all the information
        # to execute the next pages
        op_payload['button_label'] = ugettext('Send')
        op_payload['valuerange'] = 2
        op_payload['step'] = 2
        request.session[action_session_dictionary] = op_payload

        return redirect('action:item_filter')

    # Go straight to the final step.
    return email_action_done(request, op_payload)


@user_passes_test(is_instructor)
def email_action_done(request, payload=None):
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
        payload = get_action_payload(request)

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
    request.session[action_session_dictionary] = {}
    request.session.save()

    # Successful processing.
    return render(request,
                  'action/action_done.html',
                  {'log_id': log_item.id, 'download': export_wf})


@user_passes_test(is_instructor)
def zip_action(request, pk):
    """
    Request data to create a zip file. Form asking for file name pattern.
    :param request: HTTP request (GET)
    :param pk: Action key
    :return: HTTP response
    """

    # Get the workflow and action
    wflow_action = get_workflow_action(request, pk)

    # If nothing found, return
    if not wflow_action:
        return redirect(reverse('action:index'))

    # Extract workflow and action
    workflow, action = wflow_action

    if action.action_type != Action.PERSONALIZED_TEXT:
        # Incorrect type of action.
        return redirect(reverse('action:index'))

    # Get the payload from the session, and if not, use the given one
    op_payload = get_action_payload(request)
    if not op_payload:
        op_payload = {'action_id': action.id,
                      'prev_url': reverse('action:zip_action',
                                          kwargs={'pk': action.id}),
                      'post_url': reverse('action:zip_done')}
        request.session[action_session_dictionary] = op_payload
        request.session.save()

    # Create the form to ask for the email subject and other information
    form = ZipActionForm(
        request.POST or None,
        column_names=[x.name for x in workflow.columns.all()],
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
                      'action/action_zip_step1.html',
                      {'action': action,
                       'num_msgs': num_msgs,
                       'form': form})

    # Request is a POST and is valid

    # Collect information from the form and store it in op_payload
    op_payload['item_column'] = form.cleaned_data['participant_column']
    op_payload['user_fname_column'] = form.cleaned_data.get('user_fname_column',
                                                            None)
    op_payload['file_suffix'] = form.cleaned_data['file_suffix']
    op_payload['zip_for_moodle'] = form.cleaned_data.get('zip_for_moodle',
                                                         False)
    op_payload['confirm_users'] = form.cleaned_data['confirm_users']
    op_payload['exclude_values'] = []

    if op_payload['confirm_users']:
        # Create a dictionary in the session to carry over all the information
        # to execute the next pages
        op_payload['button_label'] = ugettext('Create ZIP')
        op_payload['valuerange'] = 2
        op_payload['step'] = 2
        request.session[action_session_dictionary] = op_payload

        return redirect('action:item_filter')

    # Go straight to the final step.
    return zip_action_done(request, op_payload)


@user_passes_test(is_instructor)
def zip_action_done(request, payload=None):
    """
    Final step. Create the zip object, send it for download and render the DONE
    page.

    :param request: HTTP request (GET)
    :param payload: Dictionary containing all the required parameters. If
    empty, the dictionary is taken from the session.
    :return: HTTP response
    """

    # Get the payload from the session if not given
    if payload is None:
        payload = get_action_payload(request)

        # If there is no payload, something went wrong.
        if payload is None:
            # Something is wrong with this execution. Return to action table.
            messages.error(request, _('Incorrect ZIP action invocation.'))
            return redirect('action:index')
    else:
        # Store the payload in the session for the next step
        request.session[action_session_dictionary] = payload

    # Get the information from the payload
    action = Action.objects.get(pk=payload['action_id'])
    participant_column = payload['item_column']
    user_fname_column = payload.get('user_fname_column', None)
    file_suffix = payload['file_suffix']
    zip_for_moodle = payload['zip_for_moodle']
    exclude_values = payload['exclude_values']

    # Log the event
    log_item = Log.objects.register(request.user,
                                    Log.DOWNLOAD_ZIP_ACTION,
                                    action.workflow,
                                    {'action': action.name,
                                     'action_id': action.id,
                                     'user_fname_column': user_fname_column,
                                     'participant_column': participant_column,
                                     'file_suffix': file_suffix,
                                     'zip_for_moodle': zip_for_moodle,
                                     'exclude_values': exclude_values})

    # Update the last_execution_log
    action.last_executed_log = log_item
    action.save()

    # Successful processing.
    return render(request,
                  'action/action_zip_done.html', {})


@user_passes_test(is_instructor)
def action_zip_export(request):
    """
    Create a zip with the personalised text and return it as response

    :param request: Request object with a Dictionary with all the required
    information
    :return: Response (download)
    """

    # Get the payload from the session if not given
    payload = get_action_payload(request)

    # If there is no payload, something went wrong.
    if not payload:
        # Something is wrong with this execution. Return to action table.
        messages.error(request, _('Incorrect ZIP action invocation.'))
        return redirect('action:index')

    # Get the information from the payload
    action = Action.objects.get(pk=payload['action_id'])
    user_fname_column = payload['user_fname_column']
    participant_column = payload['item_column']
    file_suffix = payload['file_suffix']
    if not file_suffix:
        file_suffix = 'feedback.html'
    zip_for_moodle = payload['zip_for_moodle']
    exclude_values = payload['exclude_values']

    # Obtain the personalised text
    # Invoke evaluate_action
    # Returns: [ (HTML, None, column name value) ] or String error!
    result = evaluate_action(action,
                             column_name=participant_column,
                             exclude_values=exclude_values)

    # Check the type of the result to see if it was successful
    if not isinstance(result, list):
        # Something went wrong. The result contains a message
        messages.error(request, _('Unable to generate zip:') + result)
        return redirect('action:index')

    if not result:
        # Result is an empty list. There is nothing to include in the ZIP
        messages.error(request, _('The resulting ZIP is empty'))
        return redirect('action:index')

    if user_fname_column:
        # Get the user_fname_column values
        user_fname_data = get_table_cursor(
            action.workflow.get_data_frame_table_name(),
            None,
            column_names=[user_fname_column]
        ).fetchall()

        # Data list combining messages, full name and participant (assuming
        # participant columns has format "Participant [number]"
        data_list = [(x[0], str(y[0]), str(x[1]))
                     for x, y in zip(result, user_fname_data)]
    else:
        # No user_fname_column given
        data_list = [(x[0], None, str(x[1])) for x in result]

    # Loop over the result
    files = []
    for msg_body, user_fname, part_id in data_list:
        html_text = html_body.format(msg_body)
        files.append((user_fname, part_id, html_text))

    # Create the file name template
    if zip_for_moodle:
        file_name_template = \
            '{user_fname}_{part_id}_assignsubmission_file_{file_suffix}'
    else:
        if user_fname_column:
            file_name_template = '{part_id}_{user_fname}_{file_suffix}'
        else:
            file_name_template = '{part_id}_{file_suffix}'

    # Create the ZIP and return it for download
    sbuf = BytesIO()
    zf = zipfile.ZipFile(sbuf, 'w')
    for user_fname, part_id, msg_body in files:
        if zip_for_moodle:
            # If a zip for Moodle, field is Participant [number]. Take the
            # number
            part_id = part_id.split()[1]

        fdict = {'user_fname': user_fname,
                 'part_id': part_id,
                 'file_suffix': file_suffix}
        zf.writestr(file_name_template.format(**fdict), str(msg_body))
    zf.close()

    suffix = datetime.now().strftime('%y%m%d_%H%M%S')
    # Attach the compressed value to the response and send
    compressed_content = sbuf.getvalue()
    response = HttpResponse(compressed_content)
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = \
        'attachment; filename="ontask_zip_action_{0}.zip"'.format(suffix)
    response['Content-Length'] = str(len(compressed_content))

    # Reset object to carry action info throughout dialogs
    request.session[action_session_dictionary] = {}
    request.session.save()

    return response


def run_json_action(request, workflow, action):
    """
    Request data to send JSON objects. Form asking for...
    :param request: HTTP request (GET)
    :param workflow: workflow being processed
    :param action: Action begin run
    :return: HTTP response
    """

    # Get the payload from the session, and if not, use the given one
    op_payload = get_action_payload(request)
    if not op_payload:
        op_payload = {'action_id': action.id,
                      'prev_url': reverse('action:run',
                                          kwargs={'pk': action.id}),
                      'post_url': reverse('action:json_done')}
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
                       'form': form,
                       'valuerange': range(2),
                       'rows_all_false': action.get_row_all_false_count()})

    # Request is a POST and is valid

    # Collect the information from the form
    op_payload['item_column'] = form.cleaned_data['key_column']
    op_payload['confirm_items'] = form.cleaned_data['key_column'] != ''
    op_payload['token'] = form.cleaned_data['token']

    if op_payload['confirm_items']:
        # Create a dictionary in the session to carry over all the information
        # to execute the next pages
        op_payload['button_label'] = ugettext('Send')
        op_payload['valuerange'] = 2
        op_payload['step'] = 2
        request.session[action_session_dictionary] = op_payload

        return redirect('action:item_filter')

    # Go straight to the final step.
    return json_done(request, op_payload)


@user_passes_test(is_instructor)
def json_done(request, payload=None):
    """
    Final step. Create the log object, queue the operation request,
    and render the DONE page.

    :param request: HTTP request (GET)
    :param payload: Dictionary containing all the required parameters. If
    empty, the dictionary is taken from the session.
    :return: HTTP response
    """

    # Get the payload from the session if not given
    if payload is None:
        payload = get_action_payload(request)

        # If there is no payload, something went wrong.
        if payload is None:
            # Something is wrong with this execution. Return to action table.
            messages.error(request, _('Incorrect JSON action invocation.'))
            return redirect('action:index')

    # Get the information from the payload
    action = Action.objects.get(pk=payload['action_id'])
    token = payload['token']
    key_column = payload['item_column']
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
    request.session[action_session_dictionary] = {}
    request.session.save()

    # Successful processing.
    return render(request, 'action/action_done.html', {'log_id': log_item.id})


def run_canvas_email_action(request, workflow, action):
    """
    Request data to send JSON objects. Form asking for...
    :param request: HTTP request (GET)
    :param workflow: workflow being processed
    :param action: Action begin run
    :return: HTTP response
    """
    # Get the payload from the session, and if not, use the given one
    op_payload = get_action_payload(request)
    if not op_payload:
        op_payload = {
            'action_id': action.id,
            'prev_url': reverse('action:run',
                                kwargs={'pk': action.id}),
            'post_url': reverse('action:canvas_get_or_set_oauth_token')
        }
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
            _('Unable to send Canvas emails due to a misconfiguration. '
              'Ask your system administrator to enable message queueing.'))
        return redirect(reverse('action:index'))

    # Create the form to ask for the email subject and other information
    form = CanvasEmailActionForm(
        request.POST or None,
        column_names=[x.name for x in workflow.columns.filter(is_key=True)],
        action=action,
        op_payload=op_payload
    )

    # Process the GET or invalid
    if request.method == 'GET' or not form.is_valid():
        # Get the number of rows from the action
        filter_obj = action.get_filter()
        num_msgs = filter_obj.n_rows_selected if filter_obj else workflow.nrows

        # Render the form
        return render(request,
                      'action/request_canvas_email_data.html',
                      {'action': action,
                       'num_msgs': num_msgs,
                       'form': form,
                       'valuerange': range(2),
                       'rows_all_false': action.get_row_all_false_count()})

    # Requet is a POST and is valid

    # Collect the information from the form
    op_payload['subject'] = form.cleaned_data['subject']
    op_payload['item_column'] = form.cleaned_data['key_column']
    op_payload['confirm_items'] = form.cleaned_data['confirm_items']
    op_payload['export_wf'] = form.cleaned_data['export_wf']
    op_payload['target_url'] = form.cleaned_data.get('target_url')
    if not op_payload['target_url']:
        op_payload['target_url'] = \
            next(iter(ontask_settings.CANVAS_INFO_DICT.keys()))
    op_payload['exclude_values'] = []

    if op_payload['confirm_items']:
        # Create a dictionary in the session to carry over all the information
        # to execute the next pages
        op_payload['valuerange'] = 2
        op_payload['step'] = 2
        op_payload['button_label'] = ugettext('Send')
        request.session[action_session_dictionary] = op_payload

        return redirect('action:item_filter')

    # Go straight to the token request step
    return canvas_get_or_set_oauth_token(request)


@user_passes_test(is_instructor)
def canvas_get_or_set_oauth_token(request):
    """
    Function that checks if the user has a Canvas OAuth token. If there is a
    token, the function goes straight to send the messages. If not, the OAuth
    process starts.

    :param request: Request object to process
    :param payload: Object with all the parameters (may be in the session)
    :return:
    """

    # Get the payload from the session
    payload = get_action_payload(request)
    if not payload:
        # Something is wrong with this execution. Return to the action table.
        messages.error(request, _('Incorrect canvas oauth request invocation.'))
        return redirect('action:index')

    # Get the information from the payload
    oauth_instance = payload.get('target_url')
    if not oauth_instance:
        messages.error(request, _('Internal error. Empty OAuth Instance name'))
        return redirect('action:index')

    oauth_info = ontask_settings.CANVAS_INFO_DICT.get(oauth_instance)
    if not oauth_info:
        messages.error(request, _('Internal error. Invalid OAuth Dict element'))
        return redirect('action:index')

    # At this point we have the correct information about the Canvas instance
    # to use. Check if we have the token
    token = OnTaskOAuthUserTokens.objects.filter(
        user=request.user,
        instance_name=oauth_instance
    ).first()

    if not token:
        # There is no token, authentication has to take place for the first time
        return get_initial_token_step1(request,
                                       oauth_info,
                                       reverse('action:canvas_email_done'))

    # Check if the token is valid
    now = datetime.now(pytz.timezone(ontask_settings.TIME_ZONE))
    dead = token.valid_until - \
           timedelta(seconds=ontask_settings.CANVAS_TOKEN_EXPIRY_SLACK)
    if now > dead:
        try:
            refresh_token(token, oauth_instance, oauth_info)
        except Exception as e:
            # Something went wrong when refreshing the token
            messages.error(request, str(e))
            return redirect('action:index')

    return redirect('action:canvas_email_done')


@user_passes_test(is_instructor)
def canvas_email_done(request, payload=None):
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
        payload = get_action_payload(request)

        # If there is no payload, something went wrong.
        if payload is None:
            # Something is wrong with this execution. Return to action table.
            messages.error(request,
                           _('Incorrect canvas email action invocation.'))
            return redirect('action:index')

    # Get the information from the payload
    action = Action.objects.get(pk=payload['action_id'])
    subject = payload['subject']
    email_column = payload['item_column']
    export_wf = payload['export_wf']
    exclude_values = payload['exclude_values']
    target_url = payload['target_url']

    # Log the event
    log_item = Log.objects.register(request.user,
                                    Log.SCHEDULE_CANVAS_EMAIL_EXECUTE,
                                    action.workflow,
                                    {'action': action.name,
                                     'action_id': action.id,
                                     'email_column': email_column,
                                     'exclude_values': exclude_values,
                                     'from_email': request.user.email,
                                     'target_url': target_url,
                                     'status': 'Preparing to execute',
                                     'subject': subject})

    # Send the emails!
    # send_canvas_email_messages(request.user.id,
    send_canvas_email_messages.delay(request.user.id,
                                     action.id,
                                     subject,
                                     email_column,
                                     exclude_values,
                                     target_url,
                                     log_item.id)

    # Reset object to carry action info throughout dialogs
    request.session[action_session_dictionary] = {}
    request.session.save()

    # Successful processing.
    return render(request,
                  'action/action_done.html',
                  {'log_id': log_item.id, 'download': export_wf})


@csrf_exempt
@user_passes_test(is_instructor)
def preview_next_all_false_response(request, pk, idx):
    """
    Previews the message that has all rows incorrect in the position next to
    the one specified by idx

    The function uses the list stored in rows_all_false and finds the next
    index in that list (or the first one if it is the last. It then invokes
    the preview_response method

    :param request: HTTP Request object
    :param pk: Primary key of the action
    :param idx:
    :return:
    """

    # To include in the JSON response
    data = dict()

    # Action being used
    try:
        action = Action.objects.get(id=pk)
    except ObjectDoesNotExist:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('home')
        return JsonResponse(data)

    # Get the list of indeces
    idx_list = action.rows_all_false

    if not idx_list:
        # If empty, or None, something went wrong.
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('home')
        return JsonResponse(data)

    # Search for the next element bigger than idx
    next_idx = next((x for x in idx_list if x > idx), None)

    if not next_idx:
        # If nothing found, then take the first element
        next_idx = idx_list[0]

    # Return the rendering of the given element
    return preview_response(request, pk, next_idx, action)


@csrf_exempt
@user_passes_test(is_instructor)
def preview_response(request, pk, idx, action=None):
    """
    HTML request and the primary key of an action to preview one of its
    instances. The request must provide and additional parameter idx to
    denote which instance to show.

    :param request: HTML request object
    :param pk: Primary key of the an action for which to do the preview
    :param idx: Index of the reponse to preview
    :param action: Might have been fetched already
    :return:
    """

    # To include in the JSON response
    data = dict()

    if not action:
        # Action being used
        try:
            action = Action.objects.get(id=pk)
        except ObjectDoesNotExist:
            data['form_is_valid'] = True
            data['html_redirect'] = reverse('home')
            return JsonResponse(data)

    # Get the workflow to obtain row numbers
    workflow = get_workflow(request, action.workflow.id)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('home')
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

    # Obtain the dictionary with the condition evaluation
    condition_evaluation = action.get_condition_evaluation(row_values)

    all_false = False
    if action.conditions.count():
        # If there are conditions, check if they are all false
        all_false = all([not value
                         for key, value in condition_evaluation.items()])

    # Get the dictionary containing column names, attributes and condition
    # valuations:
    context = action.get_evaluation_context(row_values, condition_evaluation)

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
    if action_content is None:
        action_content = \
            _("Error while retrieving content for student {0}").format(idx)
    else:
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

    if action.action_type == Action.PERSONALIZED_CANVAS_EMAIL or \
            action.action_type == Action.PERSONALIZED_JSON:
        action_content = escape(action_content)

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
                          'show_values': show_values,
                          'all_false': all_false},
                         request=request)

    return JsonResponse(data)
