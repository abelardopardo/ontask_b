"""Views to move columns and restrict values."""

from django import http
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import OnTaskServiceException
from ontask.column import forms, services
from ontask.core import (
    ColumnView, JSONFormResponseMixin, UserIsInstructor, WorkflowView,
    ajax_required)
from ontask.dataops import pandas


@method_decorator(ajax_required, name='dispatch')
class ColumnMoveView(UserIsInstructor, WorkflowView):
    """Move a column using two params: from_name and to_name."""

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        from_name = request.POST.get('from_name')
        to_name = request.POST.get('to_name')
        if not from_name or not to_name:
            return http.JsonResponse({})

        from_col = self.workflow.columns.filter(name=from_name).first()
        to_col = self.workflow.columns.filter(name=to_name).first()

        if not from_col or not to_col:
            return http.JsonResponse({})

        from_col.reposition_and_update_df(to_col.position)

        return http.JsonResponse({})


class ColumnMoveTopView(UserIsInstructor, ColumnView):
    """Move column to the first position."""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        column = self.get_object()
        # The column object has been correctly obtained
        if column.position > 1:
            column.reposition_and_update_df(1)

        return redirect('column:index')


class ColumnMoveBottomView(UserIsInstructor, ColumnView):
    """Move column to the last position."""
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        # The column and workflow objects have been correctly obtained
        if self.column.position < self.workflow.ncols:
            self.column.reposition_and_update_df(self.workflow.ncols)

        return redirect('column:index')


@method_decorator(ajax_required, name='dispatch')
class ColumnRestrictValuesView(
    UserIsInstructor,
    JSONFormResponseMixin,
    ColumnView,
    generic.DetailView
):
    """Restrict values in this column to one of those already present."""

    http_method_names = ['get', 'post']
    template_name = 'column/includes/partial_column_restrict.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        df = pandas.load_table(self.workflow.get_data_frame_table_name())
        context['values'] = ', '.join([
            str(item)
            for item in sorted(df[self.object.name].dropna().unique())])
        return context

    def get(self, request, *args, **kwargs):
        # First get the object
        self.object = self.get_object()
        # If the columns is unique, and it is the only one, we cannot allow
        # the operation
        if self.object.is_key:
            messages.error(request, _('You cannot restrict a key column'))
            return http.JsonResponse(
                {'html_redirect': reverse('column:index')})
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # First get the object
        self.object = self.get_object()
        try:
            services.restrict_column(request.user, self.object)
        except OnTaskServiceException as exc:
            exc.message_to_error(request)

        return http.JsonResponse({'html_redirect': reverse('column:index')})


class ColumnSelectView(
    UserIsInstructor,
    JSONFormResponseMixin,
    WorkflowView,
    generic.FormView,
):
    """Select a subset of columns to process further."""

    http_method_names = ['get', 'post']
    form_class = forms.ColumnSelectForm
    template_name = 'column/includes/partial_select.html'
    wf_pk_related = 'columns'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['columns'] = self.workflow.columns.all()
        return kwargs
