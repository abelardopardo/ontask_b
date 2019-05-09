# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os

from django.conf import settings
from django.shortcuts import reverse

import test
from dataops.pandas import load_table
from workflow.models import Workflow


class EmailActionTracking(test.OnTaskTestCase):
    fixtures = ['simple_email_action']
    filename = os.path.join(
        settings.BASE_DIR(),
        'action',
        'fixtures',
        'simple_email_action.sql'
    )

    trck_tokens = [
        "eyJhY3Rpb24iOjIsInNlbmRlciI6Imluc3RydWN0b3IwMUBib2d1cy5jb20iLCJ0by"
        "I6InN0dWRlbnQwMUBib2d1cy5jb20iLCJjb2x1bW5fdG8iOiJlbWFpbCIsImNvbHVtbl"
        "9kc3QiOiJFbWFpbFJlYWRfMSJ9:1hCeQr:oax6nggj9kBkSdz1oFXfYVz8R4I",
        "eyJhY3Rpb24iOjIsInNlbmRlciI6Imluc3RydWN0b3IwMUBib2d1cy5jb20iLCJ0byI6I"
        "nN0dWRlbnQwMkBib2d1cy5jb20iLCJjb2x1bW5fdG8iOiJlbWFpbCIsImNvbHVtbl9kc3Q"
        "iOiJFbWFpbFJlYWRfMSJ9:1hCeQr:nLzLJRAGgiJhZWyJ-D6oGXlIY_E",
        "eyJhY3Rpb24iOjIsInNlbmRlciI6Imluc3RydWN0b3IwMUBib2d1cy5jb20iLCJ0byI6In"
        "N0dWRlbnQwM0Bib2d1cy5jb20iLCJjb2x1bW5fdG8iOiJlbWFpbCIsImNvbHVtbl9kc3Qi"
        "OiJFbWFpbFJlYWRfMSJ9:1hCeQr:5LuQISOvahDaiYuOYUufdfYRT_o"
    ]

    wflow_name = 'wflow1'
    wflow_desc = 'description text for workflow 1'
    wflow_empty = 'The workflow does not have data'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        test.pg_restore_table(cls.filename)

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    # Test that tracking hits are properly stored.
    def test_tracking(self):
        # Repeat the checks two times to test if they are accumulating
        for idx in range(1, 3):
            # Iterate over the tracking items
            for trck in self.trck_tokens:
                self.client.get(reverse('trck') + '?v=' + trck)

            # Get the workflow and the data frame
            workflow = Workflow.objects.get(name=self.wflow_name)
            df = load_table(workflow.get_data_frame_table_name())

            # Check that the results have been updated in the DB (to 1)
            for uemail in [x[1] for x in test.user_info
                           if x[1].startswith('student')]:
                self.assertEqual(
                    int(df.loc[df['email'] == uemail, 'EmailRead_1'].values[0]),
                    idx
                )
