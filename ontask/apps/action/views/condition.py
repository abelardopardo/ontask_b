# -*- coding: utf-8 -*-

"""Functions for Condition CRUD."""
from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views import generic

from ontask.apps.action.forms import ConditionForm, FilterForm
from ontask.apps.action.models import Action, Condition
from ontask.apps.dataops.formula import EVAL_TXT, evaluate_formula, get_variables
from ontask.apps.logs.models import Log
from ontask.decorators import ajax_required, get_action, get_condition
from ontask.permissions import UserIsInstructor, is_instructor
from ontask.apps.workflow.models import Workflow


def save_condition_form(
    request: HttpRequest,
    form,
    template_name: str,
    action: Action,
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
        condition.action = action
        condition.is_filter = is_filter
        condition.save()
        condition.columns.set(action.workflow.columns.filter(
            name__in=get_variables(condition.formula),
        ))

        # If the request has the 'action_content' field, update the action
        action_content = request.POST.get('action_content')
        if action_content:
            action.set_text_content(action_content)

        propagate_changes(condition, form.changed_data, form.old_name, is_new)

        # Store the type of event to log
        if is_new:
            if is_filter:
                log_type = Log.FILTER_CREATE
            else:
                log_type = Log.CONDITION_CREATE
        else:
            if is_filter:
                log_type = Log.FILTER_UPDATE
            else:
                log_type = Log.CONDITION_UPDATE

        # Log the event
        Log.objects.register(
            request.user,
            log_type,
            action.workflow,
            {
                'id': condition.id,
                'name': condition.name,
                'selected_rows': condition.n_rows_selected,
                'formula': evaluate_formula(condition.formula, EVAL_TXT),
            })

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

    form_class = None

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

    form_class = FilterForm

    template_name = 'action/includes/partial_filter_addedit.html'


@user_passes_test(is_instructor)
@ajax_required
@get_condition(pf_related='columns', is_filter=True)
def edit_filter(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    condition: Optional[Condition] = None,
) -> JsonResponse:
    """Edit the filter of an action through AJAX.

    :param request: HTTP request

    :param pk: condition ID

    :return: AJAX response
    """
    # Render the form with the Condition information
    return save_condition_form(
        request,
        FilterForm(
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
    workflow: Optional[Workflow] = None,
    condition: Optional[Condition] = None,
) -> JsonResponse:
    """Handle the AJAX request to delete a filter.

    :param request: AJAX request

    :param pk: Filter ID

    :return: AJAX response
    """
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

    # Log the event
    formula = evaluate_formula(condition.formula, EVAL_TXT)

    Log.objects.register(
        request.user,
        Log.FILTER_DELETE,
        condition.action.workflow,
        {
            'id': condition.id,
            'name': condition.name,
            'selected_rows': condition.n_rows_selected,
            'formula': formula,
        },
    )

    # Get the action object for further processing
    action = condition.action

    # Perform the delete operation
    condition.delete()

    # Number of selected rows now needs to be updated in all remaining
    # conditions
    action.update_n_rows_selected()
    action.rows_all_false = None
    action.save()

    return JsonResponse({'html_redirect': ''})


class ConditionCreateView(ConditionFilterCreateView):
    """Handle AJAX requests to create a non-filter condition."""

    form_class = ConditionForm

    template_name = 'action/includes/partial_condition_addedit.html'


@user_passes_test(is_instructor)
@ajax_required
@get_condition(pf_related=['columns'])
def edit_condition(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    condition: Optional[Condition] = None,
) -> JsonResponse:
    """Handle the AJAX request to edit a condition.

    :param request: AJAX request

    :param pk: Condition ID

    :return: AJAX reponse
    """
    # Render the form with the Condition information
    return save_condition_form(
        request,
        ConditionForm(
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
    workflow: Optional[Workflow] = None,
    condition: Optional[Condition] = None,
) -> JsonResponse:
    """Handle the AJAX request to delete a condition.

    :param request: HTTP request

    :param pk: condition or filter id

    :return: AJAX response to render
    """
    # Treat the two types of requests
    if request.method == 'POST':
        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            condition.action.set_text_content(action_content)
            condition.action.save()

        formula = evaluate_formula(condition.formula, EVAL_TXT)

        Log.objects.register(
            request.user,
            Log.CONDITION_DELETE,
            condition.action.workflow,
            {'id': condition.id,
             'name': condition.name,
             'formula': formula})

        # Perform the delete operation
        condition.delete()

        # Reset the count of number of rows with all conditions false
        condition.action.rows_all_false = None
        condition.action.save()

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
