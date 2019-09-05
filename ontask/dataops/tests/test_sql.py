# -*- coding: utf-8 -*-


import datetime
import io
import os

from rest_framework import status

import test

import pandas as pd
from django.conf import settings

from ontask.dataops.forms.upload import load_df_from_csvfile
from ontask.dataops.formula import EVAL_EXP, EVAL_TXT, evaluate_formula
from ontask.dataops.pandas import (
    get_subframe, load_table, perform_dataframe_upload_merge, store_table,
)
from ontask.dataops.sql import get_rows
from ontask.models import Action, Workflow


class DataopsSQLQueries(test.OnTaskTestCase):
    fixtures = ['test_merge']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'test_merge.sql'
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workflow = None

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    def test_delete_table(self):
        """Test invokation of delete table"""
        # Get the workflow first
        self.workflow = Workflow.objects.all().first()

        # JSON POST request for workflow delete
        resp = self.get_response(
            'workflow:delete',
            method='POST',
            url_params={'wid': self.workflow.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue(Workflow.objects.count() == 0)
