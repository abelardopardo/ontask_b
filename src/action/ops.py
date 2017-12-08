# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

import logs.ops
from action.evaluate import evaluate_row
from action.forms import EnterActionIn, field_prefix
from action.models import Action
from dataops import pandas_db


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

    # Get the columns attached to the action
    columns = action.columns.all()

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
                       'Data not found in the table')
        return redirect(reverse('action:run', kwargs={'pk': action.id }))

    # Bind the form with the existing data
    form = EnterActionIn(request.POST or None,
                         columns=columns,
                         values=row_pairs.values())
    # Create the context
    context = {'form': form, 'action': action}

    if request.method == 'GET' or not form.is_valid():
        return render(request, 'action/run_row.html', context)

    # Correct POST request!
    if not form.has_changed():
        if not is_inst:
            return render(request, 'thanks.html', {})

        return redirect(reverse('action:run', kwargs={'pk': action.id}))

    # Post with different data. # Update content in the DB
    set_fields = []
    set_values = []
    where_field = None
    where_value = None
    log_payload = []
    # Create the SET name = value part of the query
    for idx, column in enumerate(columns):
        value = form.cleaned_data[field_prefix + '%s' % idx]
        if column.is_key:
            if not where_field:
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
    # User_instance has the record used for verification
    action_content = evaluate_row(action, (user_attribute_name,
                                           user.email))

    # If the action content is empty, forget about it
    if action_content is None:
        raise Http404

    # Log the event
    logs.ops.put(
        user,
        'action_served_execute',
        workflow=action.workflow,
        payload={'action': action.name,
                 'action_id': action.id}
    )

    # Respond the whole thing
    return HttpResponse(action_content)


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
        column_names = [c.name for c in old_action.columns.all()]
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
