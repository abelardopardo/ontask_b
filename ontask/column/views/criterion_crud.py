# -*- coding: utf-8 -*-

"""Views for create/update columns that are criteria in a rubric."""

from django import http
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import OnTaskServiceException, models
from ontask.column import forms, services
from ontask.core import (
    ActionView, ColumnConditionView, JSONFormResponseMixin,
    UserIsInstructor, ajax_required)


@method_decorator(ajax_required, name='dispatch')
class ColumnCriterionCreateView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
    generic.FormView
):
    """Add a new criteria to an action.

    If it is the first criteria, the form simply asks for a question with a
    non-empty category field.

    If it is not the first criteria, then the criteria are fixed by the
    previous elements in the rubric.
    """

    http_method_names = ['get', 'post']
    form_class = forms.CriterionForm
    template_name = 'workflow/includes/partial_criterion_add_edit.html'
    pf_related = 'column_condition_pair'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['other_criterion'] = self.object.column_condition_pair.first()
        kwargs['workflow'] = self.workflow
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.action_type != models.Action.RUBRIC_TEXT:
            messages.error(
                request,
                _('Operation only valid or Rubric actions'),
            )
            return http.JsonResponse({'html_redirect': ''})

        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            self.object.set_text_content(action_content)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Get the action first
        action = self.get_object()

        column = form.save(commit=False)
        try:
            services.add_column_to_workflow(
                self.request.user,
                self.workflow,
                column,
                form.initial_valid_value,
                models.Log.ACTION_RUBRIC_CRITERION_ADD,
                action)
            form.save_m2m()
        except OnTaskServiceException as exc:
            exc.message_to_error(self.request)
            exc.delete()

        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ColumnCriterionEditView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ColumnConditionView,
    generic.FormView,
):
    """Edit a criterion in a rubric."""

    http_method_names = ['get', 'post']
    form_class = forms.CriterionForm
    template_name = 'workflow/includes/partial_criterion_add_edit.html'
    pf_related = ['action', 'column']

    def dispatch(self, request, *args, **kwargs):
        # Set the cc_tuple object
        self.object = self.get_object()
        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            self.object.action.set_text_content(action_content)

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        action = self.object.action
        column = self.object.column

        kwargs['workflow'] = action.workflow
        kwargs['other_criterion'] = action.column_condition_pair.exclude(
            column=column.id).first()
        kwargs['instance'] = column
        return kwargs

    def form_valid(self, form):
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        column = form.save(commit=False)
        services.update_column(
            self.request.user,
            self.workflow,
            column,
            form.old_name,
            form.old_position,
            self.object,
            models.Log.ACTION_RUBRIC_CRITERION_EDIT)
        form.save_m2m()

        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ColumnCriterionDeleteView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ColumnConditionView,
    generic.DeleteView,
):
    """Delete a criterion in a rubric."""

    http_method_names = ['get', 'post']
    template_name = 'workflow/includes/partial_criterion_delete.html'
    s_related = ['column', 'action']

    def delete(self, request, *args, **kwargs):
        cc_tuple = self.get_object()
        cc_tuple.log(
            request.user,
            models.Log.ACTION_RUBRIC_CRITERION_DELETE)
        cc_tuple.action.rubric_cells.filter(column=cc_tuple.column).delete()
        cc_tuple.delete()

        return http.JsonResponse({'html_redirect': ''})


@method_decorator(ajax_required, name='dispatch')
class ColumnCriterionInsertView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ActionView,
):
    """Add an existing column as rubric criteria."""

    http_method_names = ['post']
    wf_pf_related = 'columns'
    pf_related = 'column_condition_pair'

    def post(self, request, *args, **kwargs):
        action = self.get_object()
        # If the request has the 'action_content', update the action
        action_content = request.POST.get('action_content')
        if action_content:
            action.set_text_content(action_content)

        criteria = action.column_condition_pair.all()
        column = self.workflow.columns.filter(pk=kwargs['cpk']).first()
        if not column or criteria.filter(column=column).exists():
            messages.error(
                request,
                _('Incorrect invocation of criterion insert operation.'),
            )
            return http.JsonResponse({'html_redirect': ''})

        if (
            criteria
            and set(column.categories) != set(criteria[0].column.categories)
        ):
            messages.error(
                request,
                _('Criterion does not have the correct levels of attainment'),
            )
            return http.JsonResponse({'html_redirect': ''})

        if not criteria and len(column.categories) == 0:
            messages.error(
                request,
                _('The column needs to have a fixed set of possible values'),
            )
            return http.JsonResponse({'html_redirect': ''})

        acc = models.ActionColumnConditionTuple.objects.create(
            action=action,
            column=column)

        acc.log(request.user, models.Log.ACTION_RUBRIC_CRITERION_ADD)

        # Refresh the page to show the column in the list.
        return http.JsonResponse({'html_redirect': ''})
