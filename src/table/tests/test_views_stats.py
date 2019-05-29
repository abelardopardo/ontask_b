# -*- coding: utf-8 -*-

"""Test the views for the scheduler pages."""

import os

from django.conf import settings
from django.urls import reverse

from dataops.pandas import get_table_row_by_index
from table.views.stats import (
    stat_column, stat_column_json, stat_table_view,
    stat_row_view,
)
import test


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
        resp = self.get_response('table:stat_table', stat_table_view)
        self.assertEqual(resp.status_code, 200)

        # GEt the visualization of the view
        view = self.workflow.views.get(name='simple view')
        resp = self.get_response(
            'table:stat_table_view',
            stat_table_view,
            {'pk': view.id})
        self.assertEqual(resp.status_code, 200)

        # Get one of the rows
        r_val = get_table_row_by_index(self.workflow, None, 1)
        resp = self.get_response(
            'table:stat_row',
            stat_row_view,
            req_params={'key': 'email', 'val': r_val['email']})
        self.assertEqual(resp.status_code, 200)

        # Get one of the rows from one of the views
        resp = self.get_response(
            'table:stat_row_view',
            stat_row_view,
            {'pk': view.id},
            req_params={'key': 'email', 'val': r_val['email']})
        self.assertEqual(resp.status_code, 200)

        # Get one of the columns
        col = self.workflow.columns.get(name='age')
        # Get the column visualization
        resp = self.get_response(
            'table:stat_column',
            stat_column,
            {'pk': col.id})
        self.assertEqual(resp.status_code, 200)

        # Get the JSON column visualization for a modal
        col = self.workflow.columns.get(name='one')
        resp = self.get_response(
            'table:stat_column_JSON',
            stat_column_json,
            {'pk': col.id},
            is_ajax=True)
        self.assertEqual(resp.status_code, 200)

