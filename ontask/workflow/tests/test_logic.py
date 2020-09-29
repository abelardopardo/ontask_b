# -*- coding: utf-8 -*-

"""Test workflow basic operations"""
import gzip
from io import BytesIO
import os
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.parsers import JSONParser

from ontask import models, tests
from ontask.tests.compare import compare_workflows
from ontask.workflow import services


class WorkflowImportExport(
    tests.SimpleWorkflowExportFixture,
    tests.OnTaskTestCase,
):
    """Test import export functionality."""

    def test(self):
        """Test the export functionality."""
        # Get the only workflow
        workflow = models.Workflow.objects.get(name='wflow1')

        # Export data only
        response = services.do_export_workflow(
            workflow,
            workflow.actions.all())

        self.assertEqual(
            response.get('Content-Type'),
            'application/octet-stream')
        self.assertEqual(response['Content-Transfer-Encoding'], 'binary')
        self.assertTrue(
            response.get('Content-Disposition').startswith(
                'attachment; filename="ontask_workflow'
            )
        )

        # Process the file
        data_in = gzip.GzipFile(fileobj=BytesIO(response.content))
        data = JSONParser().parse(data_in)

        # Compare the data with the current workflow
        self.assertEqual(workflow.actions.count(), len(data['actions']))
        self.assertEqual(workflow.nrows, data['nrows'])
        self.assertEqual(workflow.ncols, data['ncols'])
        self.assertEqual(workflow.attributes, data['attributes'])


class WorkflowImportExportCycle(
    tests.InitialDBFixture,
    tests.OnTaskTestCase,
):
    gz_filename = os.path.join(
        settings.BASE_DIR(),
        'initial_workflow.gz')
    tmp_filename = os.path.join('tmp')

    wflow_name = 'initial workflow'
    wflow_name2 = 'initial workflow2'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workflow = None

    def test(self):
        # Obtain user
        user = get_user_model().objects.filter(
            email='instructor01@bogus.com'
        ).first()

        # User must exist
        self.assertIsNotNone(user, 'User instructor01@bogus.com not found')

        # Workflow must not exist
        self.assertFalse(
            models.Workflow.objects.filter(
                user__email='instructor01@bogus.com',
                name=self.wflow_name
            ).exists(),
            'A workflow with this name already exists')

        with open(self.gz_filename, 'rb') as f:
            services.do_import_workflow_parse(user, self.wflow_name, f)

        # Get the new workflow
        workflow = models.Workflow.objects.filter(name=self.wflow_name).first()
        self.assertIsNotNone(workflow, 'Incorrect import operation')

        # Do the export now
        filename = os.path.join(tempfile.gettempdir(), 'ontask_tests.gz')
        zbuf = services.do_export_workflow_parse(
            workflow,
            workflow.actions.all())
        zbuf.seek(0)
        with open(filename, 'wb') as f:
            shutil.copyfileobj(zbuf, f, length=131072)

        # Import again!
        with open(filename, 'rb') as f:
            services.do_import_workflow_parse(user, self.wflow_name2, f)

        # Do the export now
        workflow2 = models.Workflow.objects.filter(
            name=self.wflow_name2).first()
        self.assertIsNotNone(workflow, 'Incorrect import operation')

        compare_workflows(workflow, workflow2)


class WorkflowDelete(tests.TestMergeFixture, tests.OnTaskTestCase):
    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):
        """Test invocation of delete table"""
        # Get the workflow first
        self.workflow = models.Workflow.objects.all().first()

        # JSON POST request for workflow delete
        resp = self.get_response(
            'workflow:delete',
            method='POST',
            url_params={'wid': self.workflow.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue(models.Workflow.objects.count() == 0)
        self.workflow = None
