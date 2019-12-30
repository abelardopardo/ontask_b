# -*- coding: utf-8 -*-

"""Test views to show the timeline."""
import os

from django.conf import settings
from rest_framework import status

from ontask import tests


class ActionViewTimeline(tests.OnTaskTestCase):
    """Test the view to show the timeline for actions."""

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

    def test_view_timeline(self):
        """Run sequence of request to the timeline view."""
        action = self.workflow.actions.get(name='Midterm comments')
        column = action.workflow.columns.get(name='email')

        # Step 1 Get the page. Should be empty
        resp = self.get_response('action:timeline')
        self.assertTrue(status.is_success(resp.status_code))
        self.assertIn(
            'No action executions have been registered',
            str(resp.content))

        # Step 2 send POST to execute one action
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'cc_email': 'user01@bogus.com user02@bogus.com',
                'bcc_email': 'user03@bogus.com user04@bogus.com',
                'item_column': column.pk,
                'subject': 'message subject'})
        self.assertTrue(status.is_success(resp.status_code))

        # Step 3 Get the page. Should have information about one execution
        resp = self.get_response('action:timeline')
        self.assertTrue(status.is_success(resp.status_code))
        self.assertNotIn(
            'No action executions have been registered',
            str(resp.content))
        self.assertIn(action.name, str(resp.content))

        # Step 4 Get the action timeline page.
        # Should have information about one execution
        resp = self.get_response(
            'action:timeline',
            {'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertNotIn(
            'No action executions have been registered',
            str(resp.content))
        self.assertIn(action.name, str(resp.content))

        # Step 5 send POST to execute the JSON action
        action2 = self.workflow.actions.get(name='Send JSON to remote server')
        resp = self.get_response(
            'action:run',
            url_params={'pk': action2.id},
            method='POST',
            req_params={
                'item_column': column.pk,
                'token': 'fake token'})

        # Step 6 Get the page. Should have information about two executions
        resp = self.get_response('action:timeline')
        self.assertTrue(status.is_success(resp.status_code))
        self.assertNotIn(
            'No action executions have been registered',
            str(resp.content))
        self.assertIn(action.name, str(resp.content))
        self.assertIn(action2.name, str(resp.content))

        # Step 7 Get the second action timeline page.
        # Should have information about one execution
        resp = self.get_response(
            'action:timeline',
            {'pk': action2.id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertNotIn(
            'No action executions have been registered',
            str(resp.content))
        self.assertNotIn(action.name, str(resp.content))
        self.assertIn(action2.name, str(resp.content))
