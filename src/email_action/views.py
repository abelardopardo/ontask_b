# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import datetime
import pytz

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail, send_mass_mail
from ontask import is_instructor, slugify
from django.shortcuts import get_object_or_404, redirect, reverse, render
from django.conf import settings as ontask_settings
from django.template import Context, Template

from logs import ops
from workflow.models import Workflow
from action.models import Action
from .forms import EmailActionForm
from action.views_action import preview_response
from action.evaluate import evaluate_action
from . import settings


@login_required
@user_passes_test(is_instructor)
def request_data(request, pk):
    """
    Request data to send emails. Form asking for subject line, email column,
    etc.
    :param request: HTTP request (GET)
    :param pk: Action key
    :return:
    """

    # Get the action attached to this request
    action = get_object_or_404(Action, pk=pk, workflow__user=request.user)
    workflow = Workflow.objects.get(pk=action.workflow.id)

    # Create the form to ask for the email subject and other information
    form = EmailActionForm(request.POST or None,
                           column_names=json.loads(workflow.column_names))

    # Process the POST
    if request.method == 'POST':

        if form.is_valid():

            # Send the emails!
            result = send_messages(request.user,
                                   action,
                                   form.cleaned_data['subject'],
                                   form.cleaned_data['email_column'],
                                   request.user.email,
                                   form.cleaned_data['send_confirmation'])

            if result is None:
                # Success
                return redirect('action:index')

            # Put the message returned from send_messages as form error
            form.add_error(None, result)

    # Get the number of rows from the action
    num_msgs = action.n_selected_rows
    if num_msgs == -1:
        # There is no filter in the action, so take the number of rows
        workflow = Workflow.objects.get(pk=action.workflow.id)
        num_msgs = workflow.nrows

    # Render the form
    return render(request,
                  'email_action/request_data.html',
                  {'action': action,
                   'num_msgs': num_msgs,
                   'form': form})


@login_required
@user_passes_test(is_instructor)
def preview(request, pk):
    """
    HTML request and the primary key of an action to preview one of its
    instances. The request must provide and additional parameter idx to
    denote which instance to show.

    :param request: HTML request object
    :param pk: Primary key of the an action for which to do the preview
    :return:
    """

    return preview_response(
        request,
        pk,
        'email_action/includes/partial_email_preview.html',
        'THE GIVEN SUBJECT WILL BE INSERTED HERE')

    # This function is redundant, but I thought I could include here the
    # subject, but it is too soon in the workflow and it is still unsubmitted.


def send_messages(user,
                  action,
                  subject,
                  email_column,
                  from_email,
                  send_confirmation):
    """
    Performs the submission of the emails for the given action and with the
    given subject. The subject will be evaluated also with respect to the
    rows, attributes, and conditions.
    :param user: User object that executed the action
    :param action: Action from where to take the messages
    :param subject: Email subject
    :param email_column: Name of the column from which to extract emails
    :param from_email: Email of the sender
    :param send_confirmation: Boolean to send confirmation to sender
    :return: Send the emails
    """

    # Evaluate the action string, evaluate the subject, and get the value of
    #  the email colummn.
    result = evaluate_action(action,
                             extra_string=subject,
                             column_name=email_column)

    # Check the type of the result to see if it was successful
    if not isinstance(result, list):
        # Something went wrong. The result contains a message
        return result

    # Everything seemed to work to create the messages. Fire away!
    msgs = [(x[1], x[0], from_email, [x[2]]) for x in result]

    # Boom
    try:
        send_mass_mail(msgs, fail_silently=False)
    except Exception, e:
        # Something went wrong, notify above
        return e.message

    now = datetime.datetime.now(pytz.timezone(ontask_settings.TIME_ZONE))

    # Log the events (one per email)
    context = {
        'user': user.id,
        'action': action.id,
        'email_sent_datetime': str(now),
    }
    for msg in msgs:
        context['subject'] = msg[0]
        context['body'] = msg[1]
        context['from_email'] = msg[2]
        context['to_email'] = msg[3]
        ops.put(user, 'action_email_sent', context)

    # If no confirmation email is required, done
    if not send_confirmation:
        return None

    # Creating the context for the personal email
    context = {
        'user': user,
        'action': action,
        'num_messages': len(msgs),
        'email_sent_datetime': now,
        'filter_present': action.n_selected_rows != -1,
        'num_rows': action.workflow.nrows}

    # Create template and render with context
    template = Template(settings.NOTIFICATION_TEMPLATE)
    msg = template.render(Context(context))

    # Send email out
    try:
        send_mail(settings.NOTIFICATION_SUBJECT,
                  msg,
                  settings.NOTIFICATION_SENDER,
                  [user.email])
    except Exception, e:
        return 'An error occurred when sending your notification: ' + e.message

    # Log the event
    ops.put(user, 'action_email_notify',
            {'user': user.id,
             'action': action.id,
             'num_messages': len(msgs),
             'email_sent_datetime': str(now),
             'filter_present': action.n_selected_rows != -1,
             'num_rows': action.workflow.nrows})

    return None
