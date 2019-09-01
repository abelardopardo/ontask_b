# -*- coding: utf-8 -*-

"""Test views to run ZIP actions."""

import os
import test

from django.conf import settings
from django.shortcuts import reverse
from rest_framework import status


class ActionViewRunZIP(test.OnTaskTestCase):
    """Test the view run a ZIP action."""

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

    def test_run_zip(self):
        """Run the zip action."""
        # Get the object first
        action = self.workflow.actions.get(name='Suggestions about the forum')
        # Request ZIP action execution
        resp = self.get_response('action:zip_action', {'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))

        # Post the execution request
        resp = self.get_response(
            'action:zip_action',
            {'pk': action.id},
            method='POST',
            req_params={
                'item_column': 'SID',
                'user_fname_column': 'email',
                'confirm_items': False,
                'zip_for_moodle': False,
            })
        self.assertTrue(status.is_success(resp.status_code))

    def test_run_zip_export(self):
        """Test the ZIP export view."""
        action = self.workflow.actions.get(name='Suggestions about the forum')

        resp = self.get_response(
            'action:zip_export',
            session_payload={
                'exclude_values': [],
                'prev_url': reverse('action:run', kwargs={'pk': action.id}),
                'post_url': reverse('action:zip_done'),
                'button_label': '',
                'valuerange': 0,
                'step': 0,
                'action_id': action.id,
                'item_column': 'SID',
                'user_fname_column': 'email',
                'file_suffix': '',
                'zip_for_moodle': False,
                'confirm_items': False})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(resp['Content-Type'], 'application/x-zip-compressed')
