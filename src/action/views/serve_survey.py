# -*- coding: utf-8 -*-

"""View to serve an action through a URL provided to learners."""

import json
import random
from typing import List, Mapping, Tuple

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from action.evaluate import get_action_evaluation_context, get_row_values
from action.forms import FIELD_PREFIX, EnterActionIn
from action.models import Action, ActionColumnConditionTuple
from dataops.sql.row_queries import update_row
from logs.models import Log
from ontask.permissions import has_access
from ontask.views import ontask_handler404


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
        log_item = Log.objects.register(
            request.user,
            Log.SURVEY_INPUT,
            action.workflow,
            {'id': action.workflow.id,
             'name': action.workflow.name,
             'action': action.name,
             'action_id': action.id,
             'new_values': json.dumps(dict(zip(row_keys, row_values)))})

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


def extract_survey_questions(
    action: Action, user_seed: str,
) -> List[ActionColumnConditionTuple]:
    """Extract the set of questions to include in a survey.

    :param action: Action being executed
    :param user_seed: Seed so that it can be replicated several times and
    is user dependent
    :return: List of ColumnCondition pairs
    """
    # Get the active columns attached to the action
    colcon_items = [
        pair for pair in action.column_condition_pair.all()
        if pair.column.is_active
    ]

    if action.shuffle:
        # Shuffle the columns if needed
        random.seed(user_seed)
        random.shuffle(colcon_items)

    return colcon_items


def survey_update_row_values(
    action: Action,
    colcon_items,
    show_key: bool,
    form_data: Mapping,
    where_field: str,
    where_value: str,
    context: Mapping,
) -> Tuple[List, List]:
    """Collect the values of the survey and update the DB.

    :param action: Action being executed
    :param colcon_items: Pairs colum - condition
    :param show_key: Should key columns be considered?
    :param form_data: Input data received in the form
    :param where_field_value: key, value to locate the user
    :param context: Condition values
    :return: Zip iterator with pairs (name, value)
    """
    keys = []
    values = []
    # Create the SET name = value part of the query
    for idx, colcon in enumerate(colcon_items):
        if colcon.column.is_key and not show_key:
            # If it is a learner request and a key column, skip
            continue

        # Skip the element if there is a condition and it is false
        if colcon.condition and not context[colcon.condition.name]:
            continue

        field_value = form_data[FIELD_PREFIX + '{0}'.format(idx)]
        if colcon.column.is_key:
            # Remember one unique key for selecting the row
            where_field = colcon.column.name
            where_value = field_value
            continue

        keys.append(colcon.column.name)
        values.append(field_value)

    # Execute the query
    update_row(
        action.workflow.get_data_frame_table_name(),
        keys,
        values,
        filter_dict={where_field: where_value},
    )

    # Recompute all the values of the conditions in each of the actions
    # TODO: Explore how to do this asynchronously (or lazy)
    for act in action.workflow.actions.all():
        act.update_n_rows_selected()

    return keys, values
