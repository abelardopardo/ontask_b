"""Functions to render the table of columns."""
from typing import Dict

from django import http
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask.core import (
    DataTablesServerSidePaging, UserIsInstructor, WorkflowView, ajax_required)


class ColumnIndexView(UserIsInstructor, WorkflowView, generic.TemplateView):
    """Show the list of columns."""

    http_method_names = ['get']
    template_name = 'column/detail.html'
    wf_pf_related = 'columns'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['table_info'] = None
        if self.workflow.has_data_frame:
            context['table_info'] = {
                'num_actions': self.workflow.actions.count()}

        # Guarantee that column position is set for backward compatibility
        columns = self.workflow.columns.all()
        if any(col.position == 0 for col in columns):
            # At least a column has index equal to zero, so reset all of them
            for idx, col in enumerate(columns):
                col.position = idx + 1
                col.save(update_fields=['position'])

        return context


@method_decorator(ajax_required, name='dispatch')
class ColumnIndexSSView(UserIsInstructor, WorkflowView):
    """Render the server side page for the table of columns.

    Return to DataTable the proper list of columns to be rendered.
    """

    http_method_names = ['post']
    wf_pf_related = 'columns'

    def column_table_server_side(
        self,
        dt_page: DataTablesServerSidePaging
    ) -> Dict:
        """Create the server side object to render a page of the table of
        columns.

        :param dt_page: Table structure for paging a query set.
        :return: Dictionary to return to the server to render the sub-page
        """
        # Get the initial set
        qs = self.workflow.columns.all()
        records_total = qs.count()
        records_filtered = records_total

        # Reorder if required
        if dt_page.order_col:
            col_name = [
                'position',
                'name',
                'description_text',
                'data_type',
                'is_key'][dt_page.order_col]
            if dt_page.order_dir == 'desc':
                col_name = '-' + col_name
            qs = qs.order_by(col_name)

        if dt_page.search_value:
            qs = qs.filter(
                Q(name__icontains=dt_page.search_value)
                | Q(data_type__icontains=dt_page.search_value))
            records_filtered = qs.count()

        # Creating the result
        final_qs = []
        for col in qs[dt_page.start:dt_page.start + dt_page.length]:
            ops_string = render_to_string(
                'column/includes/operations.html',
                {'id': col.id, 'is_key': col.is_key},
            )

            final_qs.append({
                'number': col.position,
                'name': col.name,
                'description': col.description_text,
                'type': col.get_simplified_data_type(),
                'key': '<span class="true">✔</span>' if col.is_key else '',
                'operations': ops_string,
            })

            if len(final_qs) == dt_page.length:
                break

        return {
            'draw': dt_page.draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': final_qs,
        }

    def post(self, request, *args, **kwargs):
        # Check that the POST parameter are correctly given
        dt_page = DataTablesServerSidePaging(request)
        if not dt_page.is_valid:
            return http.JsonResponse(
                {'error': _('Incorrect request. Unable to process')},
            )

        return http.JsonResponse(self.column_table_server_side(dt_page))
