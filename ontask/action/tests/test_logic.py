# -*- coding: utf-8 -*-

"""Test task logic functions."""
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from rest_framework import status

from ontask import models, tests
from ontask.action import services
from ontask.core import SessionPayload
from ontask.dataops import pandas


class EmailActionTracking(tests.SimpleEmailActionFixture, tests.OnTaskTestCase):
    """Test Email tracking."""

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

    def test(self):
        # Repeat the checks two times to test if they are accumulating
        for idx in range(1, 3):
            # Iterate over the tracking items
            for trck in self.trck_tokens:
                self.client.get(reverse('trck') + '?v=' + trck)

            # Get the workflow and the data frame
            workflow = models.Workflow.objects.get(name=self.wflow_name)
            data_frame = pandas.load_table(
                workflow.get_data_frame_table_name())

            # Check that the results have been updated in the DB (to 1)
            for uemail in [x[1] for x in tests.user_info
                           if x[1].startswith('student')]:
                self.assertEqual(
                    int(data_frame.loc[data_frame['email'] == uemail,
                               'EmailRead_1'].values[0]),
                    idx
                )


class ActionImport(tests.SimpleEmailActionFixture, tests.OnTaskTestCase):
    """Test action import."""

    def test(self):
        user = get_user_model().objects.get(email='instructor01@bogus.com')
        wflow = models.Workflow.objects.get(name=self.wflow_name)

        with open(
            os.path.join(
                settings.ONTASK_FIXTURE_DIR,
                'survey_to_import.gz'),
            'rb'
        ) as file_obj:
            services.do_import_action(user, workflow=wflow, file_item=file_obj)

        models.Action.objects.get(name='Initial survey')


class EmailActionDetectIncorrectEmail(
    tests.WrongEmailFixture,
    tests.OnTaskTestCase,
):
    """Test if incorrect email addresses are detected."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):
        user = get_user_model().objects.get(email='instructor01@bogus.com')
        wflow = models.Workflow.objects.get(name=self.wflow_name)
        email_column = wflow.columns.get(name='email')
        action = wflow.actions.first()

        # POST a send operation with the wrong email
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'item_column': email_column.pk,
                'subject': 'message subject'})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue(
            'Incorrect email address ' in str(resp.content))
        self.assertTrue(
            'incorrectemail.com' in str(resp.content))
