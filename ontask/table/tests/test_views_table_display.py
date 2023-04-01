"""Test the views for the scheduler pages."""

from django.urls import reverse
from rest_framework import status

from ontask import tests
from ontask.dataops import pandas
from ontask.table import views


class TableTestViewTableDisplay(tests.SimpleTableFixture, tests.OnTaskTestCase):
    """Test stat views."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):
        """Test the use of forms in to schedule actions."""
        # Remove is_key from column 'age'
        col = self.workflow.columns.get(name='age')
        col.is_key = False
        col.save()

        # Store the number of rows
        nrows = self.workflow.nrows

        # Get the visualization for the whole table
        resp = self.get_response('table:display')
        self.assertTrue(status.is_success(resp.status_code))

        # Get the JSON subset of the table display
        resp = self.get_response(
            'table:display_ss',
            method='POST',
            req_params={
                'draw': '1',
                'start': '0',
                'length': '10',
                'order[0][column]': '1',
                'order[0][dir]': 'asc',
                'search[value]': ''},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # GEt the display of the view
        view = self.workflow.views.get(name='simple view')
        resp = self.get_response('table:display_view', {'pk': view.id})
        self.assertTrue(status.is_success(resp.status_code))

        # Get the JSON subset of the view display
        resp = self.get_response(
            'table:display_view_ss',
            {'pk': view.id},
            method='POST',
            req_params={
                'draw': '1',
                'start': '0',
                'length': '10',
                'order[0][column]': '1',
                'order[0][dir]': 'asc',
                'search[value]': ''}, is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Delete one row of the table
        r_val = pandas.get_table_row_by_index(self.workflow, None, 1)
        resp = self.get_response(
            'table:row_delete',
            req_params={
                'key': 'email',
                'val': r_val['email']},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        req = self.factory.get(
            reverse('table:row_delete'),
            {'key': 'email', 'value': r_val['email']})

        # The POST request uses the params in the GET URL
        get_url = req.get_full_path()
        req = self.factory.post(
            get_url,
            {'key': 'email', 'value': r_val['email']},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        req = self.add_middleware(req)
        resp = views.TableRowDeleteView.as_view()(req)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.nrows, nrows - 1)

        # Incorrect post
        resp = self.get_response(
            'table:row_delete',
            method='POST',
            req_params={
                'key': 'email',
                'val': r_val['email']},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
