# -*- coding: utf-8 -*-

"""Tests the special cases for decorators."""
import os

from django.conf import settings

from ontask import tests


class DecoratorAnomalies(tests.OnTaskTestCase):
    """Test the detection of anomalies when using decorators."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'tests',
        'initial_workflow',
        'initial_workflow.sql'
    )

    wflow_name = 'wflow2'

    def test_anomalies(self):
        """Create various requests and verify that anomalies are detected."""
        pass
