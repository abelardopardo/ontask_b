# -*- coding: utf-8 -*-

"""Test plugin manager functions."""

from datetime import timedelta
import os

from django.conf import settings

from dataops.models import PluginRegistry
from dataops.views import transform_model
import test


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
        resp = self.get_response(
            'dataops:transform',
            transform_model)
        self.assertEqual(resp.status_code, 200)

        resp = self.get_response(
            'dataops:model',
            transform_model)
        self.assertEqual(resp.status_code, 200)




