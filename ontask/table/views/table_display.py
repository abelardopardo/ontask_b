"""Views related to the table element."""
from typing import Optional

from django import http
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import OnTaskServiceException
from ontask.core import (
    DataTablesServerSidePaging, JSONFormResponseMixin, UserIsInstructor,
    ViewView, WorkflowView, ajax_required)
from ontask.table import services
from ontask.visualizations.plotly import PlotlyHandler


class TableDisplayBasicView(UserIsInstructor, generic.TemplateView):
    """Render the table with the data frame."""

    http_method_names = ['get']
    template_name = 'table/display.html'
    wf_pf_related = ['actions', 'views', 'columns']

    def add_column_information(self, context, columns):
        if self.workflow.has_data_frame:
            context.update({
                'columns': columns,
                'column_types': str([''] + [col.data_type for col in columns]),
                'columns_datatables': [{'data': 'Operations'}] + [
                    {'data': col.name.replace('.', '\\.')}
                    for col in columns],
                'columns_show_stat': self.workflow.columns.filter(is_key=False),
            })
        else:
            context.update({'columns': None, 'columns_datatables': []})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'query_builder_ops': self.workflow.get_query_builder_ops(),
            'views': self.workflow.views.all(),
            'no_actions': self.workflow.actions.count() == 0,
            'vis_scripts': PlotlyHandler.get_engine_scripts(),
        })
        return context


class TableDiplayCompleteView(WorkflowView, TableDisplayBasicView):
    """View to render the complete data frame."""

    wf_pf_related = 'columns'

    def setup(self, request, *args, **kwargs):
        """Add scheduled operation attribute to view object."""
        super().setup(request, *args, **kwargs)
        if self.error_message:
            return

        if self.workflow.nrows == 0:
            self.error_message = _('Workflow has no data.')
            self.error_redirect = 'dataops:uploadmerge'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ajax_url'] = reverse('table:display_ss')
        # Add information for all the columns in the workflow
        self.add_column_information(context, self.workflow.columns.all())
        return context


class TableDisplayViewView(ViewView, TableDisplayBasicView):
    """View to render the subset of the data frame defined by View."""

    pf_related = 'columns'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ajax_url'] = reverse(
            'table:display_view_ss',
            kwargs={'pk': self.object.id})
        # Add information for all the columns in the workflow
        self.add_column_information(context, self.object.columns.all())
        return context

    def dispatch(self, request, *args, **kwargs):
        if self.error_message:
            return redirect(reverse('home'))

        self.object = self.get_object()
        if self.object.num_rows == 0:
            messages.info(
                request,
                _('Formula is excluding all rows from the table'))
        return super().dispatch(request, *args, **kwargs)


@method_decorator(ajax_required, name='dispatch')
class TableDisplayBaseSSView(UserIsInstructor, WorkflowView):
    """View to provide the server side for dataTables."""

    http_method_names = ['post']

    # Store the DtaTable server side paging object
    dt_page: Optional[DataTablesServerSidePaging] = None

    def dispatch(self, request, *args, **kwargs):
        if not self.workflow.has_data_frame:
            return http.JsonResponse(
                {'error': _('There is no data in the table')})

        self.dt_page = DataTablesServerSidePaging(request)
        if not self.dt_page.is_valid:
            return http.JsonResponse(
                {'error': _('Incorrect request. Unable to process')})

        return super().dispatch(request, *args, **kwargs)


class TableDisplayCompleteSSView(TableDisplayBaseSSView):
    """Provide server side for the complete dataTables visualization."""

    def post(self, request, *args, **kwargs):
        return http.JsonResponse(services.create_dictionary_table_display_ss(
            self.dt_page,
            self.workflow,
            self.workflow.columns.all()))


class TableDisplayViewSSView(ViewView, TableDisplayBaseSSView):
    """Provide server side for the View dataTables visualization."""

    def post(self, request, *args, **kwargs):
        view = self.get_object()
        return http.JsonResponse(services.create_dictionary_table_display_ss(
            self.dt_page,
            self.workflow,
            view.columns.all(),
            view.formula,
            view.id))


class TableRowDeleteView(
    UserIsInstructor,
    JSONFormResponseMixin,
    WorkflowView,
    generic.TemplateView
):
    """Delete a row from the workflow table."""

    template_name = 'table/includes/partial_row_delete.html'
    http_method_names = ['get', 'post']

    row_key_name = None  # To select the key to remove
    row_key_value = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.row_key_name = request.GET.get('key')
        self.row_key_value = request.GET.get('value')
        return

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'delete_key': '?key={0}&value={1}'.format(
                self.row_key_name,
                self.row_key_value)})
        return context

    def post(self, request, *args, **kwargs):
        """Perform the delete operation."""
        try:
            services.perform_row_delete(
                self.workflow,
                self.row_key_name,
                self.row_key_value)
        except OnTaskServiceException as exc:
            exc.message_to_error(request)

        return http.JsonResponse({'html_redirect': reverse('table:display')})
