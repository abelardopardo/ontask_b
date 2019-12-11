# -*- coding: utf-8 -*-

"""Functions for Condition CRUD."""
from typing import Optional, Type

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views import generic

from ontask import models
from ontask.action import forms, services
from ontask.core import (
    UserIsInstructor, ajax_required, get_action, get_condition, is_instructor)


class ConditionFilterCreateViewBase(UserIsInstructor, generic.TemplateView):
    """Class to create a filter."""

    form_class: Type[forms.FilterForm] = None

    template_name = None

    @method_decorator(user_passes_test(is_instructor))
    @method_decorator(ajax_required)
    @method_decorator(get_action(pf_related=['actions', 'columns']))
    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        """Process GET request to create a filter."""
        action = kwargs.get('action')
        form = self.form_class(action=action)
        return JsonResponse({
            'html_form': render_to_string(
                self.template_name,
                {
                    'form': form,
                    'action_id': action.id,
                    'condition': form.instance},
                request=request),
        })

    @method_decorator(user_passes_test(is_instructor))
    @method_decorator(ajax_required)
    @method_decorator(get_action(pf_related=['actions', 'columns']))
    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        """Process POST request to  create a filter."""
        del args
        action = kwargs.get('action')
        form = self.form_class(request.POST, action=action)
        if request.method == 'POST' and form.is_valid():

            if not form.has_changed():
                return JsonResponse({'html_redirect': None})

            return services.save_condition_form(
                request,
                form,
                action,
                is_filter=isinstance(self, FilterCreateView))

        return JsonResponse({
            'html_form': render_to_string(
                self.template_name,
                {
                    'form': form,
                    'action_id': action.id,
                    'condition': form.instance},
                request=request),
        })


class FilterCreateView(ConditionFilterCreateViewBase):
    """Process AJAX request to create a filter through AJAX calls."""

    form_class = forms.FilterForm
    template_name = 'action/includes/partial_filter_addedit.html'


class ConditionCreateView(ConditionFilterCreateViewBase):
    """Handle AJAX requests to create a non-filter condition."""

    form_class = forms.ConditionForm
    template_name = 'action/includes/partial_condition_addedit.html'


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
    form = forms.FilterForm(
        request.POST or None,
        instance=condition,
        action=condition.action)

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        return services.save_condition_form(
            request,
            form,
            condition.action,
            is_filter=True)

    return JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_filter_addedit.html',
            {
                'form': form,
                'action_id': condition.action.id,
                'condition': form.instance},
            request=request),
    })


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

    form = forms.ConditionForm(
        request.POST or None,
        instance=condition,
        action=condition.action)

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        return services.save_condition_form(
            request,
            form,
            condition.action,
            is_filter=False)

    return JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_condition_addedit.html',
            {
                'form': form,
                'action_id': condition.action.id,
                'condition': form.instance},
            request=request),
    })


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
