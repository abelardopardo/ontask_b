# -*- coding: utf-8 -*-

"""Views for editing Surveys and TODO_list actions."""

from django import http
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from ontask import models
from ontask.action import forms
from ontask.core import (
    ActionView, ColumnConditionView, JSONFormResponseMixin, JSONResponseMixin,
    SingleActionMixin, UserIsInstructor, ajax_required)


@method_decorator(ajax_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ActionSelectColumnSurveyView(
    UserIsInstructor,
    JSONResponseMixin,
    ActionView,
):
    """Add a column to a survey"""

    # Only AJAX Post requests allowed
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        cpk = self.kwargs.get('cpk', -1)

        if cpk == -1:
            # Unsetting key column
            self.action.column_condition_pair.filter(
                column__is_key=True).delete()
            return http.JsonResponse({'html_redirect': ''})

        # Get the column
        column = self.workflow.columns.filter(pk=cpk).first()
        if not column:
            return http.JsonResponse({'html_redirect': reverse('action:index')})

        # Parameters are correct, so add the column to the action.
        key = self.kwargs.get('key')
        if key:
            # There can only be one key column in these pairs
            self.action.column_condition_pair.filter(
                column__is_key=True).delete()

        if key != 0:
            # Insert the column in the pairs
            acc, __ = models.ActionColumnConditionTuple.objects.get_or_create(
                action=self.action,
                column=column,
                condition=None)

            acc.log(request.user, models.Log.ACTION_QUESTION_ADD)

        # Refresh the page to show the column in the list.
        return http.JsonResponse({'html_redirect': ''})


class ActionUnselectColumnSurveyView(UserIsInstructor, ActionView):
    """Unselect a column from a survey."""

    http_method_names = ['get']
    pf_related = ['actions', 'columns']

    def get(self, request, *args, **kwargs) -> http.HttpResponse:
        # Get the column
        column = self.workflow.columns.filter(pk=kwargs['cpk']).first()
        if not column:
            return redirect(reverse('action:index'))

        # Parameters are correct, so remove the column from the action.
        self.action.column_condition_pair.filter(column=column).delete()

        return redirect(reverse('action:edit', kwargs={'pk': self.action.id}))


@method_decorator(ajax_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ActionSelectConditionQuestionView(UserIsInstructor, ColumnConditionView):
    """Unselect a column from a survey."""

    http_method_names = ['post']
    pf_related = ['actions', 'columns']

    def post(self, request, *args, **kwargs):
        condition = None
        condition_pk = self.kwargs.get('condition_pk')
        if condition_pk:
            # Get the condition
            condition = self.cc_tuple.action.conditions.filter(
                pk=condition_pk).first()
            if not condition:
                return http.JsonResponse(
                    {'html_redirect': reverse('action:index')})

        # Assign the condition to the tuple and save
        self.cc_tuple.condition = condition
        self.cc_tuple.save(update_fields=['condition'])

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
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        self.action.shuffle = not self.action.shuffle
        self.action.save(update_fields=['shuffle'])

        return http.JsonResponse({'is_checked': self.action.shuffle})


@method_decorator(ajax_required, name='dispatch')
class ActionToggleQuestionChangeView(
    UserIsInstructor,
    JSONResponseMixin,
    ColumnConditionView,
):
    """Enable/Disable changes in the question."""

    # Only AJAX Post requests allowed
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        self.cc_tuple.changes_allowed = not self.cc_tuple.changes_allowed
        self.cc_tuple.save(update_fields=['changes_allowed'])
        if self.cc_tuple.action.action_type == models.Action.SURVEY:
            self.cc_tuple.log(
                request.user,
                models.Log.ACTION_QUESTION_TOGGLE_CHANGES)
        else:
            self.cc_tuple.log(
                request.user,
                models.Log.ACTION_TODOITEM_TOGGLE_CHANGES)

        return http.JsonResponse({'is_checked': self.cc_tuple.changes_allowed})


@method_decorator(ajax_required, name='dispatch')
class ActionEditDescriptionView(
    UserIsInstructor,
    JSONFormResponseMixin,
    SingleActionMixin,
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

        self.action.save(update_fields=['name', 'description_text'])
        self.action.log(self.request.user, models.Log.ACTION_UPDATE)

        return http.JsonResponse({'html_redirect': ''})
