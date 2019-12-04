# -*- coding: utf-8 -*-

"""Functions for Condition CRUD."""
from typing import Optional, Union

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views import generic

from ontask import models
from ontask.action import forms
from ontask.core import (
    UserIsInstructor, ajax_required, get_action, get_condition, is_instructor)
from ontask.dataops import formula


def save_condition_form(
    request: HttpRequest,
    form,
    template_name: str,
    action: models.Action,
    is_filter: Optional[bool] = False,
) -> JsonResponse:
    """
    Process the AJAX form to create and update conditions and filters.

    :param request: HTTP request

    :param form: Form being used to ask for the fields

    :param template_name: Template being used to render the form

    :param action: The action to which the condition is attached to

    :param is_filter: The condition is a filter

    :return: JSON response
    """
    if request.method == 'POST' and form.is_valid():

        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

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

        propagate_changes(condition, form.changed_data, form.old_name, is_new)

        # Store the type of event to log
        if is_new:
            log_type = models.Log.CONDITION_CREATE
        else:
            log_type = models.Log.CONDITION_UPDATE
        condition.log(request.user, log_type)
        return JsonResponse({'html_redirect': ''})

    # GET request or invalid form
    return JsonResponse({
        'html_form': render_to_string(
            template_name,
            {
                'form': form,
                'action_id': action.id,
                'condition': form.instance},
            request=request),
    })


class ConditionFilterCreateView(UserIsInstructor, generic.TemplateView):
    """Class to create a filter."""

    form_class: Union[forms.FilterForm, forms.ConditionForm] = None

    template_name = None

    @method_decorator(user_passes_test(is_instructor))
    @method_decorator(ajax_required)
    @method_decorator(get_action(pf_related=['actions', 'columns']))
    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        """Process GET request to create a filter."""
        return save_condition_form(
            request,
            self.form_class(action=kwargs['action']),
            self.template_name,
            kwargs.get('action'),
            is_filter=isinstance(self, FilterCreateView))

    @method_decorator(user_passes_test(is_instructor))
    @method_decorator(ajax_required)
    @method_decorator(get_action(pf_related=['actions', 'columns']))
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        """Process POST request to  create a filter."""
        del args
        return save_condition_form(
            request,
            self.form_class(request.POST, action=kwargs['action']),
            self.template_name,
            kwargs['action'],
            is_filter=isinstance(self, FilterCreateView))


class FilterCreateView(ConditionFilterCreateView):
    """Process AJAX request to create a filter through AJAX calls.

    It receives the action IDwhere the condition needs to be connected.
    """

    form_class = forms.FilterForm

    template_name = 'action/includes/partial_filter_addedit.html'


@user_passes_test(is_instructor)
@ajax_required
@get_condition(pf_related='columns', is_filter=True)
def edit_filter(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    condition: Optional[models.Condition] = None,
) -> JsonResponse:
    """Edit the filter of an action through AJAX.

    :param request: HTTP request
    :param pk: condition ID
    :param workflow: Workflow being processed
    :param condition: Filter to edit (set by the decorator)
    :return: AJAX response
    """
    del pk, workflow
    # Render the form with the Condition information
    return save_condition_form(
        request,
        forms.FilterForm(
            request.POST or None,
            instance=condition,
            action=condition.action),
        'action/includes/partial_filter_addedit.html',
        condition.action,
        is_filter=True)


@user_passes_test(is_instructor)
@ajax_required
@get_condition(pf_related='columns', is_filter=True)
def delete_filter(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    condition: Optional[models.Condition] = None,
) -> JsonResponse:
    """Handle the AJAX request to delete a filter.

    :param request: AJAX request
    :param pk: Filter ID
    :param workflow: Workflow being processed
    :param condition: Filter to edit (set by the decorator)
    :return: AJAX response
    """
    del pk, workflow
    if request.method == 'GET':
        return JsonResponse({
            'html_form': render_to_string(
                'action/includes/partial_filter_delete.html',
                {'id': condition.id},
                request=request),
        })

    # If the request has 'action_content', update the action
    action_content = request.POST.get('action_content')
    if action_content:
        condition.action.set_text_content(action_content)
        condition.action.save()

    condition.log(request.user, models.Log.CONDITION_DELETE)
    action = condition.action
    condition.delete()
    action.update_n_rows_selected()
    action.rows_all_false = None
    action.save()
    return JsonResponse({'html_redirect': ''})


class ConditionCreateView(ConditionFilterCreateView):
    """Handle AJAX requests to create a non-filter condition."""

    form_class = forms.ConditionForm
    template_name = 'action/includes/partial_condition_addedit.html'


@user_passes_test(is_instructor)
@ajax_required
@get_condition(pf_related=['columns'])
def edit_condition(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    condition: Optional[models.Condition] = None,
) -> JsonResponse:
    """Handle the AJAX request to edit a condition.

    :param request: AJAX request
    :param pk: Condition ID
    :param workflow: Workflow being processed
    :param condition: condition to edit (set by the decorator)
    :return: AJAX reponse
    """
    del pk, workflow
    # Render the form with the Condition information
    return save_condition_form(
        request,
        forms.ConditionForm(
            request.POST or None,
            instance=condition,
            action=condition.action),
        'action/includes/partial_condition_addedit.html',
        condition.action)


@user_passes_test(is_instructor)
@ajax_required
@get_condition(pf_related='columns')
def delete_condition(
    request: HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    condition: Optional[models.Condition] = None,
) -> JsonResponse:
    """Handle the AJAX request to delete a condition.

    :param request: HTTP request
    :param pk: condition or filter id
    :param workflow: Workflow being processed
    :param condition: Condition to delete (set by the decorator)
    :return: AJAX response to render
    """
    del pk, workflow
    # Treat the two types of requests
    if request.method == 'POST':
        action = condition.action
        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            action.set_text_content(action_content)
            action.save()

        condition.log(request.user, models.Log.CONDITION_DELETE)
        condition.delete()
        action.rows_all_false = None
        action.save()
        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_condition_delete.html',
            {'condition_id': condition.id},
            request=request),
    })


def propagate_changes(condition, changed_data, old_name, is_new):
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
        condition.action.save()

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
        condition.action.save()
