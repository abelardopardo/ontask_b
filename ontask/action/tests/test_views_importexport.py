# -*- coding: utf-8 -*-

"""Test views to run actions."""

import os
import test

from django.conf import settings
from django.urls import reverse
from rest_framework import status

from ontask.action.views import action_import


class ActionViewExport(test.OnTaskTestCase):
    """Test the view to run actio item filter, json and email."""

    fixtures = ['simple_workflow_two_actions']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'simple_workflow_two_actions.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'wflow2'

    def test_export_ask(self):
        """Test the export views."""
        action = self.workflow.actions.get(name='Detecting age')

        resp = self.get_response(
            'workflow:export_list_ask',
            {'wid': action.workflow.id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue('{{ registered }}' in str(resp.content))

        # Get export done
        # BROKEN!!!
        resp = self.get_response(
            'workflow:export_list_ask',
            {'wid': action.workflow.id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue('Your download will start ' in str(resp.content))

        # Get export download
        resp = self.get_response(
            'action:export',
            {'pklist': str(action.id)})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(resp['Content-Type'], 'application/octet-stream')

    def test_action_import(self):
        """Test the import ."""
        # Get request
        resp = self.get_response(
            'action:import')
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue('File containing a previously' in str(resp.content))

        file_obj = open(os.path.join(
            settings.BASE_DIR(),
            'lib',
            'surveys',
            'spq_survey.gz'),
            'rb')

        # Post request
        req = self.factory.post(
            reverse('action:import'),
            {'name': 'new action name', 'upload_file': file_obj},
        )
        req.META['HTTP_ACCEPT_ENCODING'] = 'gzip, deflate'
        req.FILES['upload_file'].content_type = 'application/x-gzip'
        req = self.add_middleware(req)
        resp = action_import(req)

        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        # Fails if the action is not there
        self.workflow.actions.get(name='new action name')
