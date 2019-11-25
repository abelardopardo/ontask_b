import json

from django import http
from django.contrib import messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.action.evaluate import (
    evaluate_row_action_out, get_action_evaluation_context, get_row_values,
)
from ontask.action.forms import EnterActionIn
from ontask.action.views.serve_survey import (
    extract_survey_questions, survey_update_row_values,
)
from ontask.core.permissions import has_access
from ontask.core.services import ontask_handler404
from ontask.models import Action, Log


def serve_action_out(
    user,
    action: models.Action,
    user_attribute_name: str,
):
    """Serve request for an action out.

    Function that given a user and an Action Out
    searches for the appropriate data in the table with the given
    attribute name equal to the user email and returns the HTTP response.
    :param user: User object making the request
    :param action: Action to execute (action out)
    :param user_attribute_name: Column to check for email
    :return:
    """
    # For the response
    payload = {'action': action.name, 'action_id': action.id}

    # User_instance has the record used for verification
    row_values = get_row_values(action, (user_attribute_name, user.email))

    # Get the dictionary containing column names, attributes and condition
    # valuations:
    context = get_action_evaluation_context(action, row_values)
    error = ''
    if context is None:
        # Log the event
        action.log(
            user,
            models.Log.ACTION_SERVED_EXECUTE,
            error=_('Error when evaluating conditions for user {0}').format(
                user.email))

        return http.HttpResponse(render_to_string(
            'action/action_unavailable.html',
            {}))

    # Evaluate the action content.
    action_content = evaluate_row_action_out(action, context)

    # If the action content is empty, forget about it
    response = action_content
    if action_content is None:
        response = render_to_string('action/action_unavailable.html', {})
        error = _('Action not enabled for user {0}').format(user.email)

    # Log the event
    action.log(
        user,
        models.Log.ACTION_SERVED_EXECUTE,
        error=_('Error when evaluating conditions for user {0}').format(
            user.email))

    # Respond the whole thing
    return http.HttpResponse(response)


def serve_survey_row(
    request: HttpRequest,
    action: Action,
    user_attribute_name: str,
) -> HttpResponse:
    """Serve a request for action in.

    Function that given a request, and an action IN, it performs the lookup
     and data input of values.

    :param request: HTTP request

    :param action:  Action In

    :param user_attribute_name: The column name used to check for email

    :return:
    """
    # Get the attribute value depending if the user is managing the workflow
    # User is instructor, and either owns the workflow or is allowed to access
    # it as shared
    manager = has_access(request.user, action.workflow)
    user_attribute_value = None
    if manager:
        user_attribute_value = request.GET.get('uatv')
    if not user_attribute_value:
        user_attribute_value = request.user.email

    # Get the dictionary containing column names, attributes and condition
    # valuations:
    context = get_action_evaluation_context(
        action,
        get_row_values(
            action,
            (user_attribute_name, user_attribute_value),
        ),
    )

    if not context:
        # If the data has not been found, flag
        if not manager:
            return ontask_handler404(request, None)

        messages.error(
            request,
            _('Data not found in the table'))
        return redirect(reverse('action:run', kwargs={'pk': action.id}))

    # Get the active columns attached to the action
    colcon_items = extract_survey_questions(action, request.user)

    # Bind the form with the existing data
    form = EnterActionIn(
        request.POST or None,
        tuples=colcon_items,
        context=context,
        values=[context[colcon.column.name] for colcon in colcon_items],
        show_key=manager)

    keep_processing = (
        request.method == 'POST'
        and form.is_valid()
        and not request.POST.get('lti_version'))
    if keep_processing:
        # Update the content in the DB
        row_keys, row_values  = survey_update_row_values(
            action,
            colcon_items,
            manager,
            form.cleaned_data,
            'email',
            request.user.email,
            context)

        # Log the event and update its content in the action
        log_item = action.log(
            request.user,
            Log.ACTION_SURVEY_INPUT,
            new_values=json.dumps(dict(zip(row_keys, row_values))))

        # Modify the time of execution for the action
        action.last_executed_log = log_item
        action.save()

        # If not instructor, just thank the user!
        if not manager:
            return render(request, 'thanks.html', {})

        # Back to running the action
        return redirect(reverse('action:run', kwargs={'pk': action.id}))

    return render(
        request,
        'action/run_survey_row.html',
        {
            'form': form,
            'action': action,
            'cancel_url': reverse(
                'action:run', kwargs={'pk': action.id},
            ) if manager else None,
        },
    )
