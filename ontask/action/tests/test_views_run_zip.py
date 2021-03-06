# -*- coding: utf-8 -*-

"""Test views to run ZIP actions."""
import os

from django.conf import settings
from django.shortcuts import reverse
from rest_framework import status

from ontask import tests


class ActionViewRunZIP(tests.OnTaskTestCase):
    """Test the view run a ZIP action."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'tests',
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
        column = action.workflow.columns.get(name='SID')
        column_fn = action.workflow.columns.get(name='email')
        # Request ZIP action execution
        resp = self.get_response('action:zip_action', {'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))

        # Post the execution request
        resp = self.get_response(
            'action:zip_action',
            {'pk': action.id},
            method='POST',
            req_params={
                'action_id': action.id,
                'item_column': column.pk,
                'user_fname_column': column_fn.pk,
                'confirm_items': False,
                'zip_for_moodle': False,
            })
        self.assertTrue(status.is_success(resp.status_code))

    def test_run_zip_export(self):
        """Test the ZIP export view."""
        action = self.workflow.actions.get(name='Suggestions about the forum')
        column = action.workflow.columns.get(name='SID')
        column_fn = action.workflow.columns.get(name='email')

        resp = self.get_response(
            'action:zip_export',
            session_payload={
                'action_id': action.id,
                'exclude_values': [],
                'prev_url': reverse('action:run', kwargs={'pk': action.id}),
                'post_url': reverse('action:run_done'),
                'button_label': '',
                'valuerange': 0,
                'step': 0,
                'item_column': column.pk,
                'user_fname_column': column_fn.pk,
                'file_suffix': '',
                'zip_for_moodle': False,
                'confirm_items': False})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(resp['Content-Type'], 'application/x-zip-compressed')
