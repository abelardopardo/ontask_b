# -*- coding: utf-8 -*-

"""Test plugin manager functions."""

from rest_framework import status

from ontask import models, tests
from ontask.dataops.plugin import OnTaskModel
from ontask.dataops.services.plugin_admin import _verify_plugin


class BogusPlugin:
    """Bogus class to be used for testing."""
    pass


class BogusPlugin2(OnTaskModel):

    def __init__(self):
        super().__init__()
        self.input_column_names = 3
        self.output_column_names = 3
        self.parameters = 3


class DataopsTransform(tests.PluginExecutionFixture, tests.OnTaskTestCase):
    """Test the transformation views."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):
        # Make sure the plugins are reloaded
        models.Plugin.objects.all().delete()
        resp = self.get_response('dataops:transform')
        self.assertTrue(status.is_success(resp.status_code))

        resp = self.get_response('dataops:model')
        self.assertTrue(status.is_success(resp.status_code))


class DataopsPluginErrors(tests.OnTaskTestCase):
    """Test the error detection for plugins."""

    # Class is subclass of OnTaskPluginAbstract
    def test_condition_1(self):
        pinobj = BogusPlugin()
        p_tests = _verify_plugin(pinobj)
        self.assertTrue(p_tests[0][0] != 'Ok')

    # Class is not documented, no fields.
    def test_condition_2(self):
        pinobj = BogusPlugin2()
        tests = _verify_plugin(pinobj)
        self.assertTrue(tests[1][0] != 'Ok')
        self.assertTrue(tests[2][0] != 'Ok')
        self.assertTrue(tests[3][0] != 'Ok')
        self.assertTrue(tests[4][0] != 'Ok')
        self.assertTrue(tests[5][0] != 'Ok')
        self.assertTrue(tests[6][0] != 'Ok')
