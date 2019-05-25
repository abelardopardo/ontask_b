# -*- coding: utf-8 -*-

"""Test the views for the scheduler pages."""

import os

from django.conf import settings
from django.urls import reverse

from dataops.pandas import get_table_row_by_index
from table.stat_views import (
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

    def test_stats_email(self):
        """Test the use of forms in to schedule actions."""
        # Get the visualization for the whole table
        req = self.get_request(
            reverse('table:stat_table'))
        resp = stat_table_view(req)
        self.assertEqual(resp.status_code, 200)

        # GEt the visualization of the view
        view = self.workflow.views.get(name='simple view')
        req = self.get_request(
            reverse('table:stat_table_view', kwargs={'pk': view.id}))
        resp = stat_table_view(req, pk=view.id)
        self.assertEqual(resp.status_code, 200)

        # Get one of the rows
        r_val = get_table_row_by_index(self.workflow, None, 1)
        req = self.get_request(
            reverse('table:stat_row'),
            req_params={'key': 'email', 'val': r_val['email']}
        )
        resp = stat_row_view(req)
        self.assertEqual(resp.status_code, 200)

        # Get one of the rows from one of the views
        req = self.get_request(
            reverse('table:stat_row_view', kwargs={'pk': view.id}),
            req_params={'key': 'email', 'val': r_val['email']}
        )
        resp = stat_row_view(req, pk=view.id)
        self.assertEqual(resp.status_code, 200)

        # Get one of the columns
        col = self.workflow.columns.get(name='one')
        # Get the column visualization
        req = self.get_request(
            reverse('table:stat_column', kwargs={'pk': col.id}))
        resp = stat_column(req, col.id)
        self.assertEqual(resp.status_code, 200)

        # Get the JSON column visualization for a modal
        req = self.get_ajax_request(
            reverse('table:stat_column_JSON', kwargs={'pk': col.id}))
        resp = stat_column_json(req, col.id)
        self.assertEqual(resp.status_code, 200)

