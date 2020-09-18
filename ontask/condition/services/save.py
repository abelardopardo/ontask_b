# -*- coding: utf-8 -*-

"""Service to manage condition operations."""
from typing import Optional

from django import http
from django.utils.html import escape

from ontask import models
from ontask.dataops import formula


def _propagate_changes(condition, changed_data, old_name):
    """Propagate changes in the condition to the rest of the action.

    If the formula has been modified, the action rows_all_false is flushed and
    the relevant conditions are updated.

    If the name has changed, the text_content in the action is updated.

    :param condition: Object being manipulated
    :param changed_data: Non-empty list of fields that have changed
    :param old_name: Previous name of the condition
    :return: Nothing
    """
    if '_formula' in changed_data:
        if condition.action:
            # Reset the counter of rows with all conditions false
            condition.action.rows_all_false = None
            condition.action.save(update_fields=['rows_all_false'])

            if not condition.is_filter:
                # Update the number of rows selected in the condition
                condition.save()

    # If condition name has changed, rename appearances in the content
    # field of the action.
    if 'name' in changed_data and condition.action:
        # Performing string substitution in the content and saving
        replacing = '{{% if {0} %}}'
        condition.action.text_content = condition.action.text_content.replace(
            escape(replacing.format(old_name)),
            escape(replacing.format(condition.name)))
        condition.action.save(update_fields=['text_content'])


def save_condition_form(
    request: http.HttpRequest,
    form,
    workflow: models.workflow,
    action: Optional[models.Action] = None,
    is_filter: Optional[bool] = False,
) -> http.JsonResponse:
    """Process the AJAX form POST to create and update conditions and filters.

    :param request: HTTP request
    :param form: Form being used to ask for the fields
    :param workflow: Workflow being processed
    :param action: The action to which the condition is attached to
    :param is_filter: The condition is a filter
    :return: JSON response
    """
    if is_filter and form.instance.id is None and action.get_filter():
        # Should not happen. Go back to editing the action
        return http.JsonResponse({'html_redirect': ''})

    is_new = form.instance.id is None

    # If the request has the 'action_content' field, update the action
    action_content = request.POST.get('action_content')
    if action_content and action:
        action.set_text_content(action_content)

    # Update fields and save the condition
    condition = form.save(commit=False)
    condition.workflow = workflow
    condition.action = action
    condition.save()
    condition.columns.set(workflow.columns.filter(
        name__in=formula.get_variables(condition.formula),
    ))
    if is_filter:
        action.filter = condition
        action.save()

    _propagate_changes(condition, form.changed_data, form.old_name)

    # Store the type of event to log
    if is_new:
        log_type = models.Log.CONDITION_CREATE
    else:
        log_type = models.Log.CONDITION_UPDATE
    condition.log(request.user, log_type)
    return http.JsonResponse({'html_redirect': ''})
