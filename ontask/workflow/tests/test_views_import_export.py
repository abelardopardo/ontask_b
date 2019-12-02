# -*- coding: utf-8 -*-

"""Test the views for import export."""
import os

from django.conf import settings
from rest_framework import status

import test


class WorkflowTestViewImportExport(test.OnTaskTestCase):
    """Test column views."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'test',
        'initial_workflow',
        'initial_workflow.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'BIOL1011'

    def test_export(self):
        """Export ask followed by export request."""
        resp = self.get_response(
            'workflow:export_ask',
            {'wid': self.workflow.id})
        self.assertTrue(status.is_success(resp.status_code))

        req_params = {
            'select_{0}'.format(idx): True
            for idx in range(self.workflow.actions.count())}
        resp = self.get_response(
            'workflow:export_ask',
            {'wid': self.workflow.id},
            method='POST',
            req_params=req_params,
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
