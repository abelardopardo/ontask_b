# -*- coding: utf-8 -*-

"""Functions for Condition CRUD."""
import copy

from typing import Optional, Type

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from ontask import models
from ontask.condition import forms, services
from ontask.core import (
    UserIsInstructor, ajax_required, get_action, get_condition, get_filter,
    is_instructor)


class ConditionBaseCreateView(UserIsInstructor, generic.TemplateView):
    """Class to create a filter."""

    form_class: Type[forms.FilterForm] = None

    template_name = None

    @method_decorator(user_passes_test(is_instructor))
    @method_decorator(ajax_required)
    @method_decorator(get_action(pf_related=['actions', 'columns']))
    def get(
        self,
        request: http.HttpRequest,
        *args,
        **kwargs
    ) -> http.JsonResponse:
        """Process GET request to create a filter."""
        action = kwargs.get('action')
        form = self.form_class(action=action)
        return http.JsonResponse({
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
    def post(
        self,
        request: http.HttpRequest,
        *args,
        **kwargs
    ) -> http.JsonResponse:
        """Process POST request to  create a filter."""
        del args
        action = kwargs.get('action')
        form = self.form_class(request.POST, action=action)
        if request.method == 'POST' and form.is_valid():

            if not form.has_changed():
                return http.JsonResponse({'html_redirect': None})

            return services.save_condition_form(
                request,
                form,
                action.workflow,
                action,
                is_filter=isinstance(self, FilterCreateView))

        return http.JsonResponse({
            'html_form': render_to_string(
                self.template_name,
                {
                    'form': form,
                    'action_id': action.id,
                    'condition': form.instance},
                request=request),
        })


class FilterCreateView(ConditionBaseCreateView):
    """Process AJAX request to create a filter through AJAX calls."""

    form_class = forms.FilterForm
    template_name = 'condition/includes/partial_filter_addedit.html'


class ConditionCreateView(ConditionBaseCreateView):
    """Handle AJAX requests to create a non-filter condition."""

    form_class = forms.ConditionForm
    template_name = 'condition/includes/partial_condition_addedit.html'


@user_passes_test(is_instructor)
@ajax_required
@get_filter(pf_related='columns')
def edit_filter(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    filter: Optional[models.Condition] = None,
) -> http.JsonResponse:
    """Edit the filter of an action through AJAX.

    :param request: HTTP request
    :param pk: condition ID
    :param workflow: Workflow being processed
    :param filter: Filter to edit (set by the decorator)
    :return: AJAX response
    """
    del pk, workflow
    # Render the form with the Condition information
    form = forms.FilterForm(
        request.POST or None,
        instance=filter,
        action=filter.action)

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        return services.save_condition_form(
            request,
            form,
            filter.action.workflow,
            filter.action,
            is_filter=True)

    return http.JsonResponse({
        'html_form': render_to_string(
            'condition/includes/partial_filter_addedit.html',
            {
                'form': form,
                'action_id': filter.action.id,
                'condition': form.instance},
            request=request)})


@user_passes_test(is_instructor)
@ajax_required
@get_action()
def set_filter(
    request: http.HttpRequest,
    pk: int,
    view_id: int,
    workflow: Optional[models.Workflow] = None,
    action: Optional[models.Action] = None,
) -> http.JsonResponse:
    """Set the formula in the view as the action filter

    :param request: HTTP request
    :param pk: View ID
    :param workflow: Workflow being processed
    :param action: Action being used
    :view_id: ID of the view to use as filter

    :return: AJAX response
    """
    del pk
    view = workflow.views.filter(pk=view_id).first()
    if not view:
        messages.error(
            request,
            _('Incorrect invocation of set view as filter'),
        )
        return http.JsonResponse({'html_redirect': ''})

    # If the action has a filter nuke it.
    filter_obj = action.get_filter()
    if filter_obj:
        filter_obj.delete_from_action()

    view.filter.action=action
    view.filter.save()

    # Action counts need to be updated.
    action.rows_all_false = None
    action.save()
    action.update_selected_rows()

    return http.JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
@ajax_required
@get_condition(pf_related=['columns'])
def edit_condition(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    condition: Optional[models.Condition] = None,
) -> http.JsonResponse:
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
            return http.JsonResponse({'html_redirect': None})

        return services.save_condition_form(
            request,
            form,
            condition.action.workflow,
            condition.action,
            is_filter=False)

    return http.JsonResponse({
        'html_form': render_to_string(
            'condition/includes/partial_condition_addedit.html',
            {
                'form': form,
                'action_id': condition.action.id,
                'condition': form.instance},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_filter(pf_related='columns')
def delete_filter(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    filter: Optional[models.Condition] = None,
) -> http.JsonResponse:
    """Handle the AJAX request to delete a filter.

    :param request: AJAX request
    :param pk: Filter ID
    :param workflow: Workflow being processed
    :param filter: Filter to edit (set by the decorator)
    :return: AJAX response
    """
    del pk, workflow
    if request.method == 'POST':
        action = filter.action
        # If the request has 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            filter.action.set_text_content(action_content)

        filter.log(request.user, models.Log.CONDITION_DELETE)
        filter.action = None
        filter.delete_from_action()
        action.rows_all_false = None
        action.save()
        action.update_selected_rows()
        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'condition/includes/partial_filter_delete.html',
            {'id': filter.id},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_condition(pf_related='columns')
def delete_condition(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
    condition: Optional[models.Condition] = None,
) -> http.JsonResponse:
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

        condition.log(request.user, models.Log.CONDITION_DELETE)
        condition.action = None
        condition.delete_from_action()
        action.rows_all_false = None
        action.save(update_fields=['rows_all_false'])
        return http.JsonResponse({'html_redirect': ''})

    return http.JsonResponse({
        'html_form': render_to_string(
            'condition/includes/partial_condition_delete.html',
            {'condition_id': condition.id},
            request=request),
    })
