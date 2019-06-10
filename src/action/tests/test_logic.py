# -*- coding: utf-8 -*-

import os
import test

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from action.models import Action
from action.views.import_export import do_import_action
from dataops.pandas import check_wf_df, load_table
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

    def test_tracking(self):
        """Test that tracking hits are properly stored."""
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
                    int(df.loc[df['email'] == uemail,
                               'EmailRead_1'].values[0]),
                    idx
                )

class ActionImport(test.OnTaskTestCase):
    fixtures = ['simple_email_action']
    filename = os.path.join(
        settings.BASE_DIR(),
        'action',
        'fixtures',
        'simple_email_action.sql'
    )

    wflow_name = 'wflow1'

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    def test_do_import(self):
        """Test the do_import_action functionality."""
        user = get_user_model().objects.get(email='instructor01@bogus.com')
        wflow = Workflow.objects.get(name=self.wflow_name)

        # with open(os.path.join(
        #     settings.BASE_DIR(),
        #     'action',
        #     'fixtures',
        #     'simple_email_action.sql'
        # ),
        #     'rb') as file_obj:
        with open ('/Users/pardosa/tmp/ontask_action_190609_193522.gz', 'rb') as file_obj:
            do_import_action(user, wflow, 'a1', file_obj)

        Action.objects.get(name='a1')
        self.assertTrue(check_wf_df(wflow))
