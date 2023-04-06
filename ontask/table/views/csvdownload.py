"""Views  to download a table or a view in CSV format."""

from django import http
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.views import generic

from ontask import models
from ontask.core import (
    UserIsInstructor, WorkflowView)
from ontask.dataops import pandas
from ontask.table import services


class TableCSVDownloadView(UserIsInstructor, WorkflowView, generic.DetailView):

    model = models.View
    is_view = False
    http_method_names = ['get']

    def get_object(self, queryset=None):
        """Get view from the workflow (if stats for view) or nothing."""
        obj = None
        if self.is_view:
            try:
                obj = self.workflow.views.get(pk=self.kwargs.get('pk'))
            except ObjectDoesNotExist:
                raise http.Http404(_("No view found matching the query."))
        return obj

    def get(self, request, *args, **kwargs):
        """Return the download response for the table/view"""
        obj = self.get_object()
        formula = None
        if obj:
            formula = obj.formula
            col_names = [col.name for col in obj.columns.all()]
        else:
            col_names = self.workflow.get_column_names()

        return services.create_response_with_csv(
            pandas.get_subframe(
                self.workflow.get_data_frame_table_name(),
                formula,
                col_names))
