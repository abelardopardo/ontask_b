# -*- coding: utf-8 -*-

"""Test the views for import export."""

import os
import test

from django.conf import settings

from action.models import Action
from dataops.pandas import load_table
import workflow.views


class WorkflowTestViewImportExport(test.OnTaskTestCase):
    """Test column views."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        '..',
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
            workflow.views.export_ask,
            {'wid': self.workflow.id})
        self.assertEqual(resp.status_code, 200)

        req_params={
            'select_{0}'.format(idx): True
            for idx in range(self.workflow.actions.count())}
        resp = self.get_response(
            'workflow:export_ask',
            workflow.views.export_ask,
            {'wid': self.workflow.id},
            method='POST',
            req_params=req_params,
            is_ajax=True)
        self.assertEqual(resp.status_code, 200)
