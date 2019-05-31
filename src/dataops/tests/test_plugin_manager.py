# -*- coding: utf-8 -*-

"""Test plugin manager functions."""

import os
import test

from django.conf import settings
from rest_framework import status

from dataops.models import PluginRegistry


class DataopsTransform(test.OnTaskTestCase):
    """Test the transformation views."""

    fixtures = ['plugin_execution']
    filename = os.path.join(
        settings.BASE_DIR(),
        'dataops',
        'fixtures',
        'plugin_execution.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'Plugin test'

    def test_transform_model(self):
        """Test the view to filter items."""
        # Make sure the plugins are reloaded
        PluginRegistry.objects.all().delete()
        resp = self.get_response('dataops:transform')
        self.assertTrue(status.is_success(resp.status_code))

        resp = self.get_response('dataops:model')
        self.assertTrue(status.is_success(resp.status_code))
