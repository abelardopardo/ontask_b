# -*- coding: utf-8 -*-

"""Test plugin manager functions."""

import os
import test

from django.conf import settings
from rest_framework import status

from ontask import models
from ontask.dataops.plugin import OnTaskModel
from ontask.dataops.services.plugin_admin import _verify_plugin


class BogusPlugin(object):
    """Bogus class to be used for testing."""
    pass


class BogusPlugin2(OnTaskModel):

    def __init__(self):
        super().__init__()
        self.input_column_names = 3
        self.output_column_names = 3
        self.parameters = 3


class DataopsTransform(test.OnTaskTestCase):
    """Test the transformation views."""

    fixtures = ['plugin_execution']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'plugin_execution.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'Plugin test'

    def test_transform_model(self):
        """Test the view to filter items."""
        # Make sure the plugins are reloaded
        models.Plugin.objects.all().delete()
        resp = self.get_response('dataops:transform')
        self.assertTrue(status.is_success(resp.status_code))

        resp = self.get_response('dataops:model')
        self.assertTrue(status.is_success(resp.status_code))


class DataopsPluginErrors(test.OnTaskTestCase):
    """Test the error detection for plugins."""

    def test_condition_1(self):
        """Class is subclass of OnTaskPlubinAbstract"""
        pinobj = BogusPlugin()
        tests = _verify_plugin(pinobj)
        self.assertTrue(tests[0][0] != 'Ok')

    def test_condition_2(self):
        """Class is not documented, no fields."""
        pinobj = BogusPlugin2()
        tests = _verify_plugin(pinobj)
        self.assertTrue(tests[1][0] != 'Ok')
        self.assertTrue(tests[2][0] != 'Ok')
        self.assertTrue(tests[3][0] != 'Ok')
        self.assertTrue(tests[4][0] != 'Ok')
        self.assertTrue(tests[5][0] != 'Ok')
        self.assertTrue(tests[6][0] != 'Ok')
