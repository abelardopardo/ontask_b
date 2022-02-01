"""Test the views for the scheduler pages."""

from rest_framework import status

from ontask import tests
from ontask.dataops import pandas
import ontask.dataops.sql.row_queries


class TableTestStatView(tests.SimpleTableFixture, tests.OnTaskTestCase):
    """Test stat views."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):
        """Test the use of forms in to schedule actions."""
        # Remove is_key from column 'age'
        col = self.workflow.columns.get(name='age')
        col.is_key = False
        col.save()

        # Get the visualization for the whole table
        resp = self.get_response('table:stat_table')
        self.assertTrue(status.is_success(resp.status_code))

        # GEt the visualization of the view
        view = self.workflow.views.get(name='simple view')
        resp = self.get_response('table:stat_table_view', {'pk': view.id})
        self.assertTrue(status.is_success(resp.status_code))

        # Get one of the rows
        r_val = ontask.dataops.sql.row_queries.get_table_row_by_index(
            self.workflow, None, 1)
        resp = self.get_response(
            'table:stat_table',
            req_params={
                'key': 'email',
                'val': r_val['email']})
        self.assertTrue(status.is_success(resp.status_code))

        # Get one of the rows from one of the views
        resp = self.get_response(
            'table:stat_table_view',
            {'pk': view.id},
            req_params={
                'key': 'email',
                'val': r_val['email']})
        self.assertTrue(status.is_success(resp.status_code))

        # Get one of the columns
        col = self.workflow.columns.get(name='age')
        # Get the column visualization
        resp = self.get_response('table:stat_column', {'pk': col.id})
        self.assertTrue(status.is_success(resp.status_code))

        # Get the JSON column visualization for a modal
        col = self.workflow.columns.get(name='one')
        resp = self.get_response(
            'table:stat_column_JSON',
            {'pk': col.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
