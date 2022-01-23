# -*- coding: utf-8 -*-

"""Views for create/rename/update/delete columns."""

from django import http
from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import OnTaskServiceException, models
from ontask.column import forms, services
from ontask.core import (
    ActionView, ColumnView, JSONFormResponseMixin, UserIsInstructor,
    ajax_required)

# These are the column operands offered through the GUI. They have immediate
# translations onto Pandas operators over dataframes. Each tuple has:
# - Pandas operation name
# - Textual description
# - List of data types that are allowed (for data type checking)
_formula_column_operands = [
    ('sum', _('sum: Sum selected columns'), ['integer', 'double']),
    (
        'prod',
        _('prod: Product of the selected columns'),
        ['integer', 'double']),
    ('max', _('max: Maximum of the selected columns'), ['integer', 'double']),
    ('min', _('min: Minimum of the selected columns'), ['integer', 'double']),
    ('mean', _('mean: Mean of the selected columns'), ['integer', 'double']),
    (
        'median',
        _('median: Median of the selected columns'),
        ['integer', 'double']),
    (
        'std',
        _('std: Standard deviation over the selected columns'),
        ['integer', 'double']),
    (
        'all',
        _('all: True when all elements in selected columns are true'),
        ['boolean']),
    (
        'any',
        _('any: True when any element in selected columns is true'),
        ['boolean']),
]


@method_decorator(ajax_required, name='dispatch')
class ColumnBasicView(UserIsInstructor, JSONFormResponseMixin):
    """Basic Column View."""

    http_method_names = ['get', 'post']
    form_class = None
    template_name = None

    def get(
        self,
        request: http.HttpRequest,
        *args,
        **kwargs
    ) -> http.JsonResponse:
        """Check if the workflow has no rows"""
        if self.workflow.nrows == 0:
            messages.error(
                request,
                _('Cannot add column to a workflow without data'),
            )
            return http.JsonResponse({'html_redirect': ''})

        return super().get(request, *args, **kwargs)


class ColumnCreateView(ColumnBasicView, ColumnView, generic.CreateView):
    """Add a column."""

    form_class = forms.ColumnAddForm
    template_name = 'column/includes/partial_addedit.html'

    def get_context_data(self, **kwargs):
        """Insert is_question and add values."""
        context = super().get_context_data(**kwargs)
        context.update({'is_question': False, 'add': True})
        return context

    def get_form_kwargs(self):
        """Add the workflow to the kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        return kwargs

    def form_valid(self, form):
        # Save the column object attached to the form
        column = form.save(commit=False)
        try:
            services.add_column_to_workflow(
                self.request.user,
                self.workflow,
                column,
                form.initial_valid_value)
            form.save_m2m()
        except OnTaskServiceException as exc:
            exc.message_to_error(self.request)
            exc.delete()

        return http.JsonResponse({'html_redirect': ''})


class ColumnQuestionAddView(ColumnBasicView, ActionView, generic.FormView):
    """Add a new column to a survey action."""

    form_class = forms.QuestionForm
    template_name = 'column/includes/partial_question_addedit.html'

    def get_form_kwargs(self):
        """Add the workflow to the kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        return kwargs

    def get_context_data(self, **kwargs):
        """Insert is_question and add values."""
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['add'] = True
        return context

    def form_valid(self, form):
        # Get the action first
        action = self.get_object()

        # Save the column object attached to the form
        column = form.save(commit=False)
        try:
            services.add_column_to_workflow(
                self.request.user,
                self.workflow,
                column,
                form.initial_valid_value,
                models.Log.ACTION_QUESTION_ADD,
                action)
            form.save_m2m()
        except OnTaskServiceException as exc:
            exc.message_to_error(self.request)
            exc.delete()

        return http.JsonResponse({'html_redirect': ''})


class ColumnTODOAddView(ColumnBasicView, ActionView, generic.FormView):
    """Add a new todo item to an action."""

    form_class = forms.TODOItemForm
    template_name = 'column/includes/partial_todoitem_addedit.html'

    def get_context_data(self, **kwargs):
        """Insert is_question and add values."""
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['add'] = True
        return context

    def get_form_kwargs(self):
        """Add the workflow to the kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        return kwargs

    def form_valid(self, form):
        # Get the action first
        action = self.get_object()

        # Save the column object attached to the form
        column = form.save(commit=False)
        try:
            services.add_column_to_workflow(
                self.request.user,
                self.workflow,
                column,
                form.initial_valid_value,
                models.Log.ACTION_TODOITEM_ADD,
                self.action)
            form.save_m2m()
        except OnTaskServiceException as exc:
            exc.message_to_error(self.request)
            exc.delete()

        return http.JsonResponse({'html_redirect': ''})


class ColumnFormulaAddView(ColumnBasicView, ColumnView, generic.CreateView):
    """Add a new formula column."""

    form_class = forms.FormulaColumnAddForm
    template_name = 'column/includes/partial_formula_add.html'
    wf_pf_selected = 'columns'

    def get_form_kwargs(self):
        """Add the workflow to the kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['operands'] = _formula_column_operands
        kwargs['columns'] = self.workflow.columns.all()
        return kwargs

    def form_valid(self, form):
        column = form.save(commit=False)
        try:
            services.add_formula_column(
                self.request.user,
                self.workflow,
                column,
                form.cleaned_data['op_type'],
                form.selected_columns)
            form.save_m2m()
        except OnTaskServiceException as exc:
            exc.message_to_error(self.request)
            exc.delete()

        return http.JsonResponse({'html_redirect': ''})


class ColumnRandomAddView(ColumnBasicView, ColumnView, generic.CreateView):
    """Create a column with random values (Modal)."""

    form_class = forms.RandomColumnAddForm
    template_name = 'column/includes/partial_random_add.html'

    def get_form_kwargs(self):
        """Add the workflow and other params to the kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        kwargs['allow_interval_as_initial'] = True
        return kwargs

    def form_valid(self, form):
        column = form.save(commit=False)
        column.workflow = self.workflow
        column.is_key = False
        column.save()

        try:
            services.add_random_column(
                self.request.user,
                self.workflow,
                column,
                form.data_frame)
            form.save_m2m()
        except services.OnTaskColumnIntegerLowerThanOneError as exc:
            form.add_error(exc.field_name, str(exc))
            return http.JsonResponse({
                'html_form': render_to_string(
                    'column/includes/partial_random_add.html',
                    {'form': form},
                    request=self.request),
            })
        except OnTaskServiceException as exc:
            exc.message_to_error(self.request)
            exc.delete()
        except Exception as exc:
            messages.error(
                self.request,
                _('Unable to add random column: {0}').format(str(exc)))

        # The form has been successfully processed
        return http.JsonResponse({'html_redirect': ''})


class ColumnEditView(ColumnBasicView, ColumnView, generic.UpdateView):
    """Edit and update a column."""

    form_class = None
    template_name = None

    def get_form_kwargs(self):
        """Add the workflow and other params to the kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['workflow'] = self.workflow
        return kwargs

    def get_context_data(self, **kwargs):
        """Insert is_question and add values."""
        context = super().get_context_data(**kwargs)
        context['add'] = False
        return context

    def form_valid(self, form):
        if not form.has_changed():
            return http.JsonResponse({'html_redirect': None})

        column = form.save(commit=False)
        services.update_column(
            self.request.user,
            self.workflow,
            column,
            form.old_name,
            form.old_position)
        form.save_m2m()

        # Done processing the correct POST request
        return http.JsonResponse({'html_redirect': ''})


class ColumnDeleteView(ColumnBasicView, ColumnView, generic.DeleteView):
    """Delete a column."""

    template_name = 'column/includes/partial_delete.html'
    wf_pf_related = ['actions', 'conditions', 'views']

    def get_context_data(self, **kwargs):
        """Insert is_question and add values."""
        context = super().get_context_data(**kwargs)
        context.update({
            # Get the conditions that need to be deleted
            'cond_to_delete': [
                cond for cond in self.workflow.conditions.all()
                if self.object in cond.columns.all()],

            # Get the action filters that need to be deleted
            'action_filter_to_delete': [
                action for action in self.workflow.actions.all()
                if
                action.filter and self.object in action.filter.columns.all()],

            # Get the views with filters that need to be deleted
            'view_filter_to_delete': [
                view for view in self.workflow.views.all()
                if view.filter and self.object in view.filter.columns.all()]})
        return context

    def delete(self, request, *args, **kwargs):
        column = self.get_object()
        services.delete_column(request.user, self.workflow, column)

        # There are various points of return
        from_url = request.META['HTTP_REFERER']
        if from_url.endswith(reverse('table:display')):
            return http.JsonResponse(
                {'html_redirect': reverse('table:display')})

        return http.JsonResponse({'html_redirect': reverse('column:index')})


class ColumnCloneView(ColumnBasicView, ColumnView, generic.DetailView):
    """"Clone a column in the table attached to a workflow."""

    template_name = 'column/includes/partial_clone.html'

    def post(self, request, *args, **kwargs):
        # Proceed to clone the column
        column = self.get_object()
        try:
            services.clone_column(request.user, column)
        except Exception as exc:
            messages.error(
                request,
                _('Unable to clone column: {0}').format(str(exc)))
            return http.JsonResponse({'html_redirect': ''})

        return http.JsonResponse({'html_redirect': ''})
