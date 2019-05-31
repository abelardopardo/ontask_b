# -*- coding: utf-8 -*-

"""Test the views for the scheduler pages."""

import os
import test

from django.conf import settings
from rest_framework import status

from dataops.pandas import get_table_row_by_index


class TableTestStatView(test.OnTaskTestCase):
    """Test stat views."""

    fixtures = ['simple_table']
    filename = os.path.join(
        settings.BASE_DIR(),
        'table',
        'fixtures',
        'simple_table.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'wflow1'

    def test_stats(self):
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
        r_val = get_table_row_by_index(self.workflow, None, 1)
        resp = self.get_response(
            'table:stat_row',
            req_params={
                'key': 'email',
                'val': r_val['email']})
        self.assertTrue(status.is_success(resp.status_code))

        # Get one of the rows from one of the views
        resp = self.get_response(
            'table:stat_row_view',
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
