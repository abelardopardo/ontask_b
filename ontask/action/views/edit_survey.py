# -*- coding: utf-8 -*-

"""Views for editing Surveys and TODO_list actions."""

from django import http
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic

from ontask import models
from ontask.action import forms
from ontask.core import (
    ActionView, ColumnConditionView, JSONFormResponseMixin, JSONResponseMixin,
    UserIsInstructor, ajax_required)


@method_decorator(ajax_required, name='dispatch')
class ActionSelectColumnSurveyView(
    UserIsInstructor,
    JSONResponseMixin,
    ActionView,
):
    """Add a column to a survey"""

    # Only AJAX Post requests allowed
    http_method_names = ['post']
    wf_pf_related = 'columns'
    pf_related = ['conditions', 'column_condition_pair']
    object = None
    select_column = False
    key_column = False

    def post(self, request, *args, **kwargs):
        action = self.get_object()

        if not self.select_column:
            # Unselecting column
            action.log(request.user, models.Log.ACTION_QUESTION_REMOVE)
            action.column_condition_pair.filter(
                column__is_key=True).delete()
            return http.JsonResponse({'html_redirect': ''})

        # Get the column
        column = self.workflow.columns.filter(pk=self.kwargs.get('cpk')).first()
        if not column:
            return http.JsonResponse({'html_redirect': reverse('action:index')})

        # Parameters are correct, so add the column to the action.
        if self.key_column:
            # There can only be one key column in these pairs
            action.column_condition_pair.filter(
                column__is_key=True).delete()

        # Insert the column in the pairs
        acc, __ = models.ActionColumnConditionTuple.objects.get_or_create(
            action=action,
            column=column)

        acc.log(request.user, models.Log.ACTION_QUESTION_ADD)

        # Refresh the page to show the column in the list.
        return http.JsonResponse({'html_redirect': ''})


class ActionUnselectColumnSurveyView(UserIsInstructor, ActionView):
    """Unselect a column from a survey."""

    http_method_names = ['post']
    wf_pf_related = ['columns']
    pf_related = 'column_condition_pair'
    object = None

    def post(self, request, *args, **kwargs) -> http.HttpResponse:
        # Get the column
        action = self.get_object()
        column = self.workflow.columns.filter(pk=kwargs['cpk']).first()
        if not column:
            return redirect(reverse('action:index'))

        action.log(request.user, models.Log.ACTION_QUESTION_REMOVE)

        # Parameters are correct, so remove the column from the action.
        action.column_condition_pair.filter(column=column).delete()

        return redirect(reverse('action:edit', kwargs={'pk': action.id}))


@method_decorator(ajax_required, name='dispatch')
class ActionSelectConditionQuestionView(UserIsInstructor, ColumnConditionView):
    """Select/Unselect a condition to show a question in a survey."""

    http_method_names = ['post']
    s_related = ['action', 'action__conditions']

    def post(self, request, *args, **kwargs):
        cc_tuple = self.get_object()
        condition = None
        condition_pk = self.kwargs.get('condition_pk')
        if condition_pk:
            # Get the condition
            condition = cc_tuple.action.conditions.filter(
                pk=condition_pk).first()
            if not condition:
                return http.JsonResponse(
                    {'html_redirect': reverse('action:index')})

        # Assign the condition to the tuple and save
        cc_tuple.condition = condition
        cc_tuple.save(update_fields=['condition'])

        # Refresh the page to show the column in the list.
        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ActionShuffleQuestionsView(
    UserIsInstructor,
    JSONResponseMixin,
    ActionView,
):
    """Toggle the shuffle questions field"""

    # Only AJAX Post requests allowed
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        action = self.get_object()
        action.shuffle = not action.shuffle
        action.save(update_fields=['shuffle'])

        return http.JsonResponse({'is_checked': action.shuffle})


@method_decorator(ajax_required, name='dispatch')
class ActionToggleQuestionChangeView(
    UserIsInstructor,
    JSONResponseMixin,
    ColumnConditionView,
):
    """Enable/Disable changes in the question."""

    # Only AJAX Post requests allowed
    http_method_names = ['post']
    s_related = 'action'

    def post(self, request, *args, **kwargs):
        cc_tuple = self.get_object()
        cc_tuple.changes_allowed = not cc_tuple.changes_allowed
        cc_tuple.save(update_fields=['changes_allowed'])
        if cc_tuple.action.action_type == models.Action.SURVEY:
            cc_tuple.log(
                request.user,
                models.Log.ACTION_QUESTION_TOGGLE_CHANGES)
        else:
            cc_tuple.log(
                request.user,
                models.Log.ACTION_TODOITEM_TOGGLE_CHANGES)

        return http.JsonResponse({'is_checked': cc_tuple.changes_allowed})


@method_decorator(ajax_required, name='dispatch')
class ActionEditDescriptionView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
    generic.UpdateView,
):
    """Edit a cell in a rubric."""
    http_method_names = ['get', 'post']
    form_class = forms.ActionDescriptionForm
    template_name = 'action/includes/partial_action_edit_description.html'

    def form_valid(self, form):
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        self.object.save(update_fields=['name', 'description_text'])
        self.object.log(self.request.user, models.Log.ACTION_UPDATE)

        return http.JsonResponse({'html_redirect': ''})
