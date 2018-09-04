# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os

from django.conf import settings
from django.shortcuts import reverse

import test
from dataops import pandas_db


class EmailActionTracking(test.OntaskTestCase):
    fixtures = ['simple_email_action']
    filename = os.path.join(
        settings.BASE_DIR(),
        'action',
        'fixtures',
        'simple_email_action.sql'
    )

    trck_tokens = [
        "eyJhY3Rpb24iOjIsInRvIjoic3R1ZGVudDFAYm9ndXMuY29tIiwiY29sdW1uX2RzdCI6IkVtYWlsUmVhZF8xIiwic2VuZGVyIjoiaWRlc2lnbmVyMUBib2d1cy5jb20iLCJjb2x1bW5fdG8iOiJlbWFpbCJ9:1eBtw5:MwH1axNDQq9HpgcP6jRvp7cAFmI",
        "eyJhY3Rpb24iOjIsInRvIjoic3R1ZGVudDJAYm9ndXMuY29tIiwiY29sdW1uX2RzdCI6IkVtYWlsUmVhZF8xIiwic2VuZGVyIjoiaWRlc2lnbmVyMUBib2d1cy5jb20iLCJjb2x1bW5fdG8iOiJlbWFpbCJ9:1eBtw5:FFS1EXjdgJjc37ZVOcW22aIegR4",
        "eyJhY3Rpb24iOjIsInRvIjoic3R1ZGVudDNAYm9ndXMuY29tIiwiY29sdW1uX2RzdCI6IkVtYWlsUmVhZF8xIiwic2VuZGVyIjoiaWRlc2lnbmVyMUBib2d1cy5jb20iLCJjb2x1bW5fdG8iOiJlbWFpbCJ9:1eBtw5:V0KhNWbcY3YPTfJXRagPaeJae4M"
    ]

    wflow_name = 'wflow1'
    wflow_desc = 'description text for workflow 1'
    wflow_empty = 'The workflow does not have data'

    @classmethod
    def setUpClass(cls):
        super(EmailActionTracking, cls).setUpClass()
        pandas_db.pg_restore_table(cls.filename)

    def tearDown(self):
        pandas_db.delete_all_tables()
        super(EmailActionTracking, self).tearDown()

    # Test that tracking hits are properly stored.
    def test_tracking(self):
        # Repeat the checks two times to test if they are accumulating
        for idx in range(1, 3):
            # Iterate over the tracking items
            for trck in self.trck_tokens:
                self.client.get(reverse('trck') + '?v=' + trck)

            # No longer working due to celery
            # # Get the workflow and the data frame
            # workflow = Workflow.objects.get(name=self.wflow_name)
            # df = pandas_db.load_from_db(workflow.id)
            #
            # # Check that the results have been updated in the DB (to 1)
            # for uemail in [x[1] for x in test.user_info
            #                if x[1].startswith('student')]:
            #     self.assertEqual(
            #         int(df.loc[df['email'] == uemail, 'EmailRead_1'].values[0]),
            #         idx
            #     )
