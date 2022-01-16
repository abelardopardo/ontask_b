# -*- coding: utf-8 -*-

"""Implementation of views providing visualisation and stats."""
from typing import Optional

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import generic

from ontask import models
from ontask.core import (
    ColumnView, JSONFormResponseMixin, UserIsInstructor,
    ajax_required, get_workflow, is_instructor)
from ontask.table import services


class ColumnStatsView(UserIsInstructor, ColumnView, generic.TemplateView):
    """Render the stat for a column."""

    template_name = 'table/stat_column.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stat_data, __, visualizations = services.get_column_visualization_items(
            self.workflow,
            self.column)

        context.update({
            'stat_data': stat_data,
            'vis_scripts': [],
            'visualizations': [viz.html_content for viz in visualizations]
        })
        return context


@method_decorator(ajax_required, name='dispatch')
class ColumnStatsModalView(JSONFormResponseMixin, ColumnStatsView):
    """Render the stat for a column to show in a modal."""

    template_name = 'table/includes/partial_column_stats_modal.html'


@user_passes_test(is_instructor)
@get_workflow(pf_related=['columns', 'views'])
def stat_table_view(
    request: http.HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Render the page with stats and visualizations for a view.

    :param request: HTTP request
    :param pk: View id to use
    :param workflow: Workflow being manipulated (set by the decorators)
    :return: Render the page
    """
    # If the workflow has no data, something went wrong, go back to the
    # workflow details page
    if workflow.nrows == 0:
        messages.error(
            request,
            _('Unable to provide visualisation without data.'))
        return redirect('worflow:detail', workflow.id)

    # Get the key/val pair to select the row (return if not consistent)
    rowselect_key = request.GET.get('key', None)
    rowselect_val = request.GET.get('val', None)
    if bool(rowselect_key) != bool(rowselect_val):
        return render(
            request,
            'error.html',
            {'message': _('Unable to visualize table row')})

    viz_items = services.get_table_visualization_items(
        workflow,
        rowselect_key,
        rowselect_val,
        pk)
    if not viz_items:
        return redirect('home')

    template, context = viz_items
    return render(request, template, context)
