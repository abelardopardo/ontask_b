# -*- coding: utf-8 -*-
"""
File with auxiliary operations needed to handle the actions, namely:
functions to process request when receiving a "serve" action, cloning
operations when cloning conditions and actions, and sending messages.
"""
from __future__ import unicode_literals, print_function

import datetime
import gzip
import random
from io import BytesIO

import pytz
from django.conf import settings as ontask_settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core import signing, mail
from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import Context, Template, TemplateSyntaxError
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.utils.translation import ugettext_lazy as _
from validate_email import validate_email

import logs.ops
from action.evaluate import evaluate_row_action_out, evaluate_action, \
    get_row_values
from action.forms import EnterActionIn, field_prefix
from action.models import Action
from dataops import pandas_db, ops
from workflow.models import Column
from workflow.serializers import ActionSelfcontainedSerializer
from . import settings


def serve_action_in(request, action, user_attribute_name, is_inst):
    """
    Function that given a request, and an action IN, it performs the lookup
     and data input of values.
    :param request: HTTP request
    :param action:  Action In
    :param user_attribute_name: The column name used to check for email
    :param is_inst: Boolean stating if the user is instructor
    :return:
    """

    # Get the attribute value
    if is_inst:
        user_attribute_value = request.GET.get('uatv', None)
    else:
        user_attribute_value = request.user.email

    # Get the active columns attached to the action
    columns = [c for c in action.columns.all() if c.is_active]
    if action.shuffle:
        # Shuffle the columns if needed
        random.seed(request.user)
        random.shuffle(columns)

    # Get the row values. User_instance has the record used for verification
    row_pairs = pandas_db.get_table_row_by_key(
        action.workflow,
        None,
        (user_attribute_name, user_attribute_value),
        [c.name for c in columns]
    )

    # If the data has not been found, flag
    if not row_pairs:
        if not is_inst:
            return render(request, '404.html', {})

        messages.error(request,
                       _('Data not found in the table'))
        return redirect(reverse('action:run', kwargs={'pk': action.id}))

    # Bind the form with the existing data
    form = EnterActionIn(request.POST or None,
                         columns=columns,
                         values=row_pairs.values(),
                         show_key=is_inst)

    cancel_url = None
    if is_inst:
        cancel_url = reverse('action:run', kwargs={'pk': action.id})

    # Create the context
    context = {'form': form,
               'action': action,
               'cancel_url': cancel_url}

    if request.method == 'GET' or not form.is_valid():
        return render(request, 'action/run_row.html', context)

    # Correct POST request!
    if not form.has_changed():
        if not is_inst:
            return redirect(reverse('action:thanks'))

        return redirect(reverse('action:run', kwargs={'pk': action.id}))

    # Post with different data. # Update content in the DB
    set_fields = []
    set_values = []
    where_field = 'email'
    where_value = request.user.email
    log_payload = []
    # Create the SET name = value part of the query
    for idx, column in enumerate(columns):
        if not is_inst and column.is_key:
            # If it is a learner request and a key column, skip
            continue

        value = form.cleaned_data[field_prefix + '%s' % idx]
        if column.is_key:
            # Remember one unique key for selecting the row
            where_field = column.name
            where_value = value
            continue

        set_fields.append(column.name)
        set_values.append(value)
        log_payload.append((column.name, value))

    pandas_db.update_row(action.workflow.id,
                         set_fields,
                         set_values,
                         [where_field],
                         [where_value])

    # Recompute all the values of the conditions in each of the actions
    for act in action.workflow.actions.all():
        act.update_n_rows_selected()

    # Log the event
    logs.ops.put(request.user,
                 'tablerow_update',
                 action.workflow,
                 {'id': action.workflow.id,
                  'name': action.workflow.name,
                  'new_values': log_payload})

    # If not instructor, just thank the user!
    if not is_inst:
        return render(request, 'thanks.html', {})

    # Back to running the action
    return redirect(reverse('action:run', kwargs={'pk': action.id}))


def serve_action_out(user, action, user_attribute_name):
    """
    Function that given a user and an Action Out
    searches for the appropriate data in the table with the given
    attribute name equal to the user email and returns the HTTP response.
    :param user: User object making the request
    :param action: Action to execute (action out)
    :param user_attribute_name: Column to check for email
    :return:
    """

    # For the response
    payload = {'action': action.name,
               'action_id': action.id}

    # User_instance has the record used for verification
    row_values = get_row_values(action,
                                (user_attribute_name, user.email))

    # Get the dictionary containing column names, attributes and condition
    # valuations:
    context = action.get_evaluation_context(row_values)
    if context is None:
        payload['error'] = \
            _('Error when evaluating conditions for user {0}').format(
                user.email
            )
        # Log the event
        logs.ops.put(
            user,
            'action_served_execute',
            workflow=action.workflow,
            payload=payload
        )
        return HttpResponse(render_to_string('action/action_unavailable.html',
                                             {}))

    # Evaluate the action content.
    action_content = evaluate_row_action_out(action, context)

    # If the action content is empty, forget about it
    response = action_content
    if action_content is None:
        response = render_to_string('action/action_unavailable.html', {})
        payload['error'] = _('Action not enabled for user {0}').format(
            user.email
        )

    # Log the event
    logs.ops.put(
        user,
        'action_served_execute',
        workflow=action.workflow,
        payload=payload
    )

    # Respond the whole thing
    return HttpResponse(response)


def clone_condition(condition, new_action=None, new_name=None):
    """
    Function to clone a condition and change action and/or name
    :param condition: Condition to clone
    :param new_action: New action to point
    :param new_name: New name
    :return: New condition
    """

    condition.id = None
    if new_action:
        condition.action = new_action
    if new_name:
        condition.name = new_name
    condition.save()

    return condition


def clone_conditions(conditions, new_action):
    """
    Function that given a set of conditions, clones them and makes them point
    to the new aciont
    :param conditions: List of conditions to clone
    :param new_action: New action to point to
    :return: Reflected in the DB
    """

    # Iterate over the conditions and clone them (no recursive call needed as
    # there are no other objects pointing to them
    for condition in conditions:
        clone_condition(condition, new_action)


def clone_action(action, new_workflow=None, new_name=None):
    """
    Function that given an action clones it and changes workflow and name
    :param action: Object to clone
    :param new_workflow: New workflow object to point
    :param new_name: New name
    :return: Cloned object
    """

    # Store the old object id before squashing it
    old_id = action.id

    # Clone
    action.id = None

    # Update some of the fields
    if new_name:
        action.name = new_name
    if new_workflow:
        action.workflow = new_workflow

    # Update
    action.save()

    # Get back the old action
    old_action = Action.objects.get(id=old_id)

    # Clone the columns field (in case of an action in).
    if not action.is_out:
        column_names = old_action.columns.all().values_list('name', flat=True)
        action.columns.clear()
        action.columns.add(
            *list(action.workflow.columns.filter(
                name__in=column_names
            )))

    # Clone the conditions
    clone_conditions(old_action.conditions.all(), action)

    # Update
    action.save()

    return action


def clone_actions(actions, new_workflow):
    """
    Function that given a set of actions, clones its content and attaches
    them to a new workflow
    :param actions: List of actions
    :param new_workflow: New workflow object
    :return: Reflected in the DB
    """

    # Iterate over the actions and clone each of them
    for action in actions:
        clone_action(action, new_workflow)


def send_messages(user,
                  action,
                  subject,
                  email_column,
                  from_email,
                  cc_email_list,
                  bcc_email_list,
                  send_confirmation,
                  track_read):
    """
    Performs the submission of the emails for the given action and with the
    given subject. The subject will be evaluated also with respect to the
    rows, attributes, and conditions.
    :param user: User object that executed the action
    :param action: Action from where to take the messages
    :param subject: Email subject
    :param email_column: Name of the column from which to extract emails
    :param from_email: Email of the sender
    :param cc_email_list: List of emails to include in the CC
    :param bcc_email_list: List of emails to include in the BCC
    :param send_confirmation: Boolean to send confirmation to sender
    :param track_read: Should read tracking be included?
    :return: Send the emails
    """

    # Evaluate the action string, evaluate the subject, and get the value of
    # the email column.
    result = evaluate_action(action,
                             extra_string=subject,
                             column_name=email_column)

    # Check the type of the result to see if it was successful
    if not isinstance(result, list):
        # Something went wrong. The result contains a message
        return result

    track_col_name = ''
    data_frame = None
    if track_read:
        data_frame = pandas_db.load_from_db(action.workflow.id)
        # Make sure the column name does not collide with an existing one
        i = 0  # Suffix to rename
        while True:
            i += 1
            track_col_name = 'EmailRead_{0}'.format(i)
            if track_col_name not in data_frame.columns:
                break

    # Update the number of filtered rows if the action has a filter (table
    # might have changed)
    cfilter = action.conditions.filter(is_filter=True).first()
    if cfilter and cfilter.n_rows_selected != len(result):
        cfilter.n_rows_selected = len(result)
        cfilter.save()

    # Set the cc_email_list and bcc_email_list to the right values
    if not cc_email_list:
        cc_email_list = []
    if not bcc_email_list:
        bcc_email_list = []

    # Check that cc and bcc contain list of valid email addresses
    if not all([validate_email(x) for x in cc_email_list]):
        return _('Invalid email address in cc email')
    if not all([validate_email(x) for x in bcc_email_list]):
        return _('Invalid email address in bcc email')

    # Everything seemed to work to create the messages.
    msgs = []
    for msg_body, msg_subject, msg_to in result:

        # If read tracking is on, add suffix for message (or empty)
        if track_read:
            # The track id must identify: action & user
            track_id = {
                'action': action.id,
                'sender': user.email,
                'to': msg_to,
                'column_to': email_column,
                'column_dst': track_col_name
            }

            track_str = \
                """<img src="https://{0}{1}{2}?v={3}" alt="" 
                    style="position:absolute; visibility:hidden"/>""".format(
                    Site.objects.get_current().domain,
                    ontask_settings.BASE_URL,
                    reverse('trck'),
                    signing.dumps(track_id)
                )
        else:
            track_str = ''

        # Get the plain text content and bundle it together with the HTML in
        # a message to be added to the list.
        text_content = strip_tags(msg_body)
        msg = EmailMultiAlternatives(
            msg_subject,
            text_content,
            from_email,
            [msg_to],
            bcc_email_list,
            cc=cc_email_list
        )
        msg.attach_alternative(msg_body + track_str, "text/html")
        msgs.append(msg)

    # Mass mail!
    try:
        connection = mail.get_connection()
        connection.send_messages(msgs)
    except Exception as e:
        # Something went wrong, notify above
        return str(e)

    # Add the column if needed
    if track_read:
        # Create the new column and store
        column = Column(
            name=track_col_name,
            workflow=action.workflow,
            data_type='integer',
            is_key=False,
            position=action.workflow.ncols + 1
        )
        column.save()

        # Increase the number of columns in the workflow
        action.workflow.ncols += 1
        action.workflow.save()

        # Initial value in the data frame and store the table
        data_frame[track_col_name] = 0
        ops.store_dataframe_in_db(data_frame, action.workflow.id)

    # Log the events (one per email)
    now = datetime.datetime.now(pytz.timezone(ontask_settings.TIME_ZONE))
    context = {
        'user': user.id,
        'action': action.id,
        'email_sent_datetime': str(now),
    }
    for msg in msgs:
        context['subject'] = msg.subject
        context['body'] = msg.body
        context['from_email'] = msg.from_email
        context['to_email'] = msg.to[0]
        logs.ops.put(user, 'action_email_sent', action.workflow, context)

    # Log the event
    logs.ops.put(
        user,
        'action_email_sent',
        action.workflow,
        {'user': user.id,
         'action': action.name,
         'num_messages': len(msgs),
         'email_sent_datetime': str(now),
         'filter_present': filter is not None,
         'num_rows': action.workflow.nrows,
         'subject': subject,
         'from_email': user.email,
         'cc_email': cc_email_list,
         'bcc_email': bcc_email_list})

    # If no confirmation email is required, done
    if not send_confirmation:
        return None

    # Creating the context for the personal email
    context = {
        'user': user,
        'action': action,
        'num_messages': len(msgs),
        'email_sent_datetime': now,
        'filter_present': filter is not None,
        'num_rows': action.workflow.nrows,
        'num_selected': cfilter.n_rows_selected if filter else -1}

    # Create template and render with context
    try:
        html_content = Template(
            str(getattr(settings, 'NOTIFICATION_TEMPLATE'))
        ).render(Context(context))
        text_content = strip_tags(html_content)
    except TemplateSyntaxError as e:
        return _('Syntax error detected in OnTask notification template '
                 '({0})').format(e.message)

    # Log the event
    logs.ops.put(
        user,
        'action_email_notify', action.workflow,
        {'user': user.id,
         'action': action.id,
         'num_messages': len(msgs),
         'email_sent_datetime': str(now),
         'filter_present': filter is not None,
         'num_rows': action.workflow.nrows,
         'subject': str(getattr(settings, 'NOTIFICATION_SUBJECT')),
         'body': text_content,
         'from_email': str(getattr(settings, 'NOTIFICATION_SENDER')),
         'to_email': [user.email]})

    # Send email out
    try:
        send_mail(
            str(getattr(settings, 'NOTIFICATION_SUBJECT')),
            text_content,
            str(getattr(settings, 'NOTIFICATION_SENDER')),
            [user.email],
            html_message=html_content)
    except Exception as e:
        return _('An error occurred when sending your notification: '
                 '{0}').format(e.message)

    return None


def do_export_action(action):
    """
    Proceed with the action export.
    :param action: Element to export.
    :return: Page that shows a confirmation message and starts the download
    """

    # Context
    context = {'workflow': action.workflow}

    # Get the info to send from the serializer
    serializer = ActionSelfcontainedSerializer(action, context=context)
    to_send = JSONRenderer().render(serializer.data)

    # Get the in-memory file to compress
    zbuf = BytesIO()
    zfile = gzip.GzipFile(mode='wb', compresslevel=6, fileobj=zbuf)
    zfile.write(to_send)
    zfile.close()

    suffix = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
    # Attach the compressed value to the response and send
    compressed_content = zbuf.getvalue()
    response = HttpResponse(compressed_content)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = \
        'attachment; filename="ontask_action_{0}.gz"'.format(suffix)
    response['Content-Length'] = str(len(compressed_content))

    return response


def do_import_action(user, workflow, name, file_item):
    """
    Receives a name and a file item (submitted through a form) and creates
    the structure of action with conditions and columns

    :param user: User record to use for the import (own all created items)
    :param workflow: Workflow object to attach the action
    :param name: Workflow name (it has been checked that it does not exist)
    :param file_item: File item obtained through a form
    :return:
    """

    try:
        data_in = gzip.GzipFile(fileobj=file_item)
        data = JSONParser().parse(data_in)
    except IOError:
        return _('Incorrect file. Expecting a GZIP file (exported workflow).')

    # Serialize content
    action_data = ActionSelfcontainedSerializer(
        data=data,
        context={'user': user, 'name': name, 'workflow': workflow}
    )

    # If anything goes wrong, return a string to show in the page.
    try:
        if not action_data.is_valid():
            return _('Unable to import action: {0}').format(action_data.errors)

        # Save the new workflow
        action = action_data.save(user=user, name=name)
    except (TypeError, NotImplementedError) as e:
        return _('Unable to import action: {0}').format(e.message)
    except serializers.ValidationError as e:
        return _('Unable to import action due to a validation error: '
                 '{0}').format(e.message)
    except Exception as e:
        return _('Unable to import action: {0}').format(e.message)

    # Success, log the event
    logs.ops.put(user,
                 'action_import',
                 workflow,
                 {'id': action.id,
                  'name': action.name})
    return None
