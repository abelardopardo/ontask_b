# -*- coding: utf-8 -*-

"""Test views to run ZIP actions."""

from django.shortcuts import reverse
from rest_framework import status

from ontask import tests


class ActionViewZIPBasic(tests.InitialWorkflowFixture, tests.OnTaskTestCase):
    """Test the view run a ZIP action."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'


class ActionViewRunZIP(ActionViewZIPBasic):
    """Test the view run a ZIP action."""

    def test(self):
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


class ActionViewRunZIPExport(ActionViewZIPBasic):
    """Test the view run a ZIP action."""

    def test(self):
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
