# -*- coding: utf-8 -*-

"""View to edit rubric actions."""

from django import http
from django.contrib import messages
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import models
from ontask.action import forms
from ontask.core import (
    ActionView, JSONFormResponseMixin, UserIsInstructor, ajax_required)


@method_decorator(ajax_required, name='dispatch')
class ActionEditRubricLOAView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
    generic.FormView,
):
    """Edit one level of attainment row in a rubric attached to an action."""
    http_method_names = ['get', 'post']
    form_class = forms.RubricLOAForm
    template_name = 'action/includes/partial_rubric_loas_edit.html'

    def get(self, request, *args, **kwargs):
        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            self.action.set_text_content(action_content)
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Add the criteria to the context for the form."""
        kwargs = super().get_form_kwargs()
        kwargs['criteria'] = [
            acc.column for acc in self.action.column_condition_pair.all()]
        return kwargs

    def form_valid(self, form) -> http.JsonResponse:
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        loas = [
            loa.strip()
            for loa in form.cleaned_data['levels_of_attainment'].split(',')]

        # Update all columns
        try:
            with transaction.atomic():
                for acc in self.action.column_condition_pair.all():
                    acc.column.set_categories(loas, validate=True)
        except Exception as exc:
            messages.error(
                self.request,
                _('Incorrect level of attainment values ({0}).').format(
                    str(exc)))

        # Log the event
        self.action.log(
            self.request.user,
            models.Log.ACTION_RUBRIC_LOA_EDIT,
            new_loas=loas)

        # Done processing the correct POST request
        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ActionEditRubricCellView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
    generic.FormView,
):
    """Edit a cell in a rubric."""
    http_method_names = ['get', 'post']
    form_class = forms.RubricCellForm
    template_name = 'action/includes/partial_rubric_cell_edit.html'

    def get(self, request, *args, **kwargs):
        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            self.action.set_text_content(action_content)
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        """Add the criteria to the context for the form."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.action.rubric_cells.filter(
            column=self.kwargs['cid'],
            loa_position=self.kwargs['loa_pos']).first()
        return kwargs

    def form_valid(self, form) -> http.JsonResponse:
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        cell = form.save(commit=False)
        if cell.id is None:
            # New cell in the rubric
            cell.action = self.action
            cell.column = self.action.workflow.columns.get(
                pk=self.kwargs['cid'])
            cell.loa_position = self.kwargs['loa_pos']
        cell.save()
        cell.log(self.request.user, models.Log.ACTION_RUBRIC_CELL_EDIT)
        return http.JsonResponse({'html_redirect': ''})
