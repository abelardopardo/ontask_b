# -*- coding: utf-8 -*-

"""Test the views for import export."""

from rest_framework import status

from ontask import tests


class WorkflowTestViewImportExport(
    tests.InitialWorkflowFixture,
    tests.OnTaskTestCase,
):
    """Test column views."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):
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
