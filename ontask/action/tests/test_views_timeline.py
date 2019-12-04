# -*- coding: utf-8 -*-

"""Test views to show the timeline."""
import os

from django.conf import settings
from rest_framework import status

import test


class ActionViewTimeline(test.OnTaskTestCase):
    """Test the view to show the timeline for actions."""

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

    def test_view_timeline(self):
        """Run sequence of request to the timeline view."""
        self.client.login(email=self.user_email, password=self.user_pwd)

        # Step 1 Get the page
        resp = self.get_response('action:timeline')
        self.assertTrue(status.is_success(resp.status_code))
