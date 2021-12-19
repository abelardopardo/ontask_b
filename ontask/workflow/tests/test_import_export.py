# -*- coding: utf-8 -*-

"""Test the views for import export."""
import os

from django.conf import settings
from rest_framework import status

from ontask import models, tests
from ontask.tests.compare import compare_workflows
from ontask.workflow import services


class WorkflowTestViewImportExport(
    tests.InitialWorkflowFixture,
    tests.OnTaskTestCase,
):
    """Test workflow export."""

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


class WorkflowTestImportExportStructure(
    tests.ViewAsFilterFixture,
    tests.OnTaskTestCase,
):
    """Test workflow import of view as filter in workflow."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):

        self.assertEqual(models.Workflow.objects.count(), 1)

        with open(
            os.path.join(settings.ONTASK_FIXTURE_DIR, 'view_as_filter.gz'),
            'rb'
        ) as f:
            services.do_import_workflow_parse(self.user, 'vaf', f)

        self.assertEqual(models.Workflow.objects.count(), 2)

        compare_workflows(
            self.workflow,
            models.Workflow.objects.get(name='vaf'))
