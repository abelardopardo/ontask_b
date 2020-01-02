# -*- coding: utf-8 -*-

"""Service to manage condition operations."""
from typing import Optional

from django.http.request import HttpRequest
from django.http.response import JsonResponse
from django.utils.html import escape

from ontask import models
from ontask.dataops import formula


def _propagate_changes(condition, changed_data, old_name, is_new):
    """Propagate changes in the condition to the rest of the action.

    If the formula has been modified, the action rows_all_false is flushed and
    the relevant conditions are updated.

    If the name has changed, the text_content in the action is updated.

    :param condition: Object being manipulated
    :param changed_data: Non-empty list of fields that have changed
    :param old_name: Previous name of the condition
    :param is_new: if the condition has just been created
    :return: Nothing
    """
    if is_new or 'formula' in changed_data:
        # Reset the counter of rows with all conditions false
        condition.action.rows_all_false = None
        condition.action.save(update_fields=['rows_all_false'])

        if condition.is_filter:
            # This update must propagate to the rest of conditions
            condition.action.update_n_rows_selected()
            condition.refresh_from_db(fields=['n_rows_selected'])
        else:
            # Update the number of rows selected in the condition
            condition.update_n_rows_selected()

    # If condition name has changed, rename appearances in the content
    # field of the action.
    if is_new or 'name' in changed_data:
        # Performing string substitution in the content and saving
        replacing = '{{% if {0} %}}'
        condition.action.text_content = condition.action.text_content.replace(
            escape(replacing.format(old_name)),
            escape(replacing.format(condition.name)))
        condition.action.save(update_fields=['text_content'])


def save_condition_form(
    request: HttpRequest,
    form,
    action: models.Action,
    is_filter: Optional[bool] = False,
) -> JsonResponse:
    """Process the AJAX form POST to create and update conditions and filters.

    :param request: HTTP request
    :param form: Form being used to ask for the fields
    :param action: The action to which the condition is attached to
    :param is_filter: The condition is a filter
    :return: JSON response
    """
    if is_filter and form.instance.id is None and action.get_filter():
        # Should not happen. Go back to editing the action
        return JsonResponse({'html_redirect': ''})

    is_new = form.instance.id is None

    # Update fields and save the condition
    condition = form.save(commit=False)
    condition.formula_text = None
    condition.action = action
    condition.is_filter = is_filter
    condition.save()
    condition.columns.set(action.workflow.columns.filter(
        name__in=formula.get_variables(condition.formula),
    ))

    # If the request has the 'action_content' field, update the action
    action_content = request.POST.get('action_content')
    if action_content:
        action.set_text_content(action_content)

    _propagate_changes(condition, form.changed_data, form.old_name, is_new)

    # Store the type of event to log
    if is_new:
        log_type = models.Log.CONDITION_CREATE
    else:
        log_type = models.Log.CONDITION_UPDATE
    condition.log(request.user, log_type)
    return JsonResponse({'html_redirect': ''})
