"""Test views to run actions."""
import os

from django.conf import settings
from django.urls import reverse
from rest_framework import status

from ontask import tests
from ontask.action import services


class ActionViewExportBasic(
    tests.SimpleWorkflowTwoActionsFixture,
    tests.OnTaskTestCase,
):
    """Basic class to test the action export view."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'


class ActionViewExport(ActionViewExportBasic):
    """Test the action export view."""

    def test(self):
        action = self.workflow.actions.get(name='Detecting age')

        resp = self.get_response(
            'workflow:export_list_ask',
            {'wid': action.workflow_id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue(action.name in str(resp.content))

        # Get export done
        resp = self.get_response(
            'workflow:export_list_ask',
            {'wid': action.workflow_id},
            method='POST',
            req_params={'select_0': True})

        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue('Your download will start ' in str(resp.content))

        # Get export download
        resp = self.get_response(
            'action:export',
            {'pklist': str(action.id)})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(resp['Content-Type'], 'application/octet-stream')


class ActionViewImport(ActionViewExportBasic):
    """Test the view to import a workflow."""

    def test(self):
        # Get request
        resp = self.get_response(
            'action:import')
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue('File containing a previously' in str(resp.content))

        file_obj = open(
            os.path.join(
                settings.BASE_DIR(),
                'lib',
                'surveys',
                'spq_survey.gz'),
            'rb')

        # Post request
        req = self.factory.post(
            reverse('action:import'),
            {'upload_file': file_obj})
        req.META['HTTP_ACCEPT_ENCODING'] = 'gzip, deflate'
        req.FILES['upload_file'].content_type = 'application/x-gzip'
        req = self.add_middleware(req)

        services.do_import_action(
            req.user,
            self.workflow,
            req.FILES['upload_file']
        )

        # Fails if the action is not there
        self.workflow.actions.get(name='SPQ')
