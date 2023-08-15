"""Implementation of views providing visualisation and stats."""

from django import http
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import generic

from ontask import models
from ontask.core import (
    ColumnView, JSONFormResponseMixin, UserIsInstructor, WorkflowView,
    ajax_required)
from ontask.dataops import sql
from ontask.table import services


class ColumnStatsView(UserIsInstructor, ColumnView, generic.DetailView):
    """Render the stat for a column."""

    template_name = 'table/stat_column.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stat_data, vs, visualizations = \
            services.get_column_visualization_items(
                self.workflow,
                self.object)

        context.update({
            'stat_data': stat_data,
            'vis_scripts': vs,
            'visualizations': [viz.html_content for viz in visualizations]
        })
        return context


@method_decorator(ajax_required, name='dispatch')
class ColumnStatsModalView(JSONFormResponseMixin, ColumnStatsView):
    """Render the stat for a column to show in a modal."""

    template_name = 'table/includes/partial_column_stats_modal.html'


class TableStatView(UserIsInstructor, WorkflowView, generic.DetailView):
    """Render page with stats and visualisations for whole table or view."""

    is_view = False
    template_name = None  # Set on a per-request basis
    model = models.View
    view = None
    wf_pf_related = ['columns', 'views']
    context_object_name = 'table_view'

    def dispatch(
            self,
            request: http.HttpRequest,
            *args,
            **kwargs
    ) -> http.JsonResponse:
        """Check if the workflow has no rows"""
        if self.error_message:
            return redirect(reverse('home'))

        if self.workflow.nrows == 0:
            messages.error(
                request,
                _('Unable to provide visualisation without data.'))
            return redirect('workflow:detail', self.workflow.id)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """Get view from the workflow (if stats for view) or nothing."""
        obj = None
        if self.is_view:
            try:
                obj = self.workflow.views.get(pk=self.kwargs.get('pk'))
            except ObjectDoesNotExist:
                raise http.Http404(_("No view found matching the query."))
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the key/val pair to select the row (return if not consistent)
        row_select_key = self.request.GET.get('key', None)
        row_select_val = self.request.GET.get('val', None)
        if bool(row_select_key) != bool(row_select_val):
            return render(
                self.request,
                'error.html',
                {'message': _('Unable to visualize table row')})

        if row_select_key:
            self.template_name = 'table/stat_row.html'
        else:
            self.template_name = 'table/stat_view.html'
        # Get the data frame and the columns
        data_frame, columns_to_view = services.get_df_and_columns(
            self.workflow,
            self.view)

        row = None
        if bool(row_select_key):
            row = sql.get_row(
                self.workflow.get_data_frame_table_name(),
                row_select_key,
                row_select_val,
                column_names=[col.name for col in columns_to_view])

        vis_scripts, visualizations = services.get_table_visualization_items(
            data_frame,
            columns_to_view,
            row)

        context.update({
            'reference_value': row_select_val,
            'vis_scripts': vis_scripts,
            'visualizations': visualizations})

        if row_select_val:
            # Add the reference value
            context['reference_value'] = row_select_val

        return context
