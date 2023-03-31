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

    :param condition: Object being manipulated (condition or filter)
    :param changed_data: Non-empty list of fields that have changed
    :param old_name: Previous name of the condition
    :return: Nothing
    """
    if '_formula' in changed_data:
        condition.update_fields()

    if condition.is_filter:
        # A filter does not have a name, thus no more changes needed.
        return

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
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Process the AJAX form POST to create and update conditions and filters.

    :param request: HTTP request
    :param form: Form being used to ask for the fields
    :param action: The action to which the condition is attached to
    :return: JSON response
    """
    is_new = form.instance.id is None

    # If the request has the 'action_content' field, update the action
    action_content = request.POST.get('action_content')
    if action_content and action:
        action.set_text_content(action_content)

    # Update fields and save the condition
    condition = form.save(commit=False)
    condition.workflow = action.workflow
    if not condition.is_filter:
        condition.action = action
    # Save object to processfurther (update row counts and column set
    condition.save()

    if condition.is_filter:
        action.filter = condition
        action.rows_all_false = None
        action.save(update_fields=['filter', 'rows_all_false'])
        action.update_selected_row_counts()

    condition.columns.set(action.workflow.columns.filter(
        name__in=formula.get_variables(condition.formula)))

    _propagate_changes(condition, form.changed_data, form.old_name)

    # Store the type of event to log
    if is_new:
        log_type = models.Log.CONDITION_CREATE
    else:
        log_type = models.Log.CONDITION_UPDATE
    condition.log(request.user, log_type)
    return http.JsonResponse({'html_redirect': ''})
