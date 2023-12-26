"""Test task logic functions."""
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.shortcuts import reverse
from rest_framework import status

from ontask.action import services
from ontask.models import Workflow, Action
from ontask.tests import (
    SimpleEmailActionFixture, OnTaskTestCase, WrongEmailFixture,
    FilterCorrectEmailsFixture, user_info)
from ontask.dataops import pandas


class EmailActionTracking(SimpleEmailActionFixture, OnTaskTestCase):
    """Test Email tracking."""

    def test(self):
        trck_tokens = [
            signing.dumps(item) for item in
            [{
                'action': 2,
                'sender': 'instructor01@bogus.com',
                'to': 'student01@bogus.com',
                'column_to': 'email',
                'column_dst': 'EmailRead_1'},
                {
                    'action': 2,
                    'sender': 'instructor01@bogus.com',
                    'to': 'student02@bogus.com',
                    'column_to': 'email',
                    'column_dst': 'EmailRead_1'},
                {
                    'action': 2,
                    'sender': 'instructor01@bogus.com',
                    'to': 'student03@bogus.com',
                    'column_to': 'email',
                    'column_dst': 'EmailRead_1'}]]

        # Repeat the checks two times to test if they are accumulating
        for idx in range(1, 3):
            # Iterate over the tracking items
            for track in trck_tokens:
                self.client.get(reverse('trck') + '?v=' + track)

            # Get the workflow and the data frame
            workflow = Workflow.objects.get(name=self.wflow_name)
            data_frame = pandas.load_table(
                workflow.get_data_frame_table_name())

            # Check that the results have been updated in the DB (to 1)
            for user_email in [
                x[1] for x in user_info if x[1].startswith('student')]:
                self.assertEqual(
                    int(
                        data_frame.loc[
                            data_frame['email'] == user_email,
                            'EmailRead_1'].values[0]),
                    idx)


class ActionImport(SimpleEmailActionFixture, OnTaskTestCase):
    """Test action import."""

    def test(self):
        user = get_user_model().objects.get(email='instructor01@bogus.com')
        wflow = Workflow.objects.get(name=self.wflow_name)

        with open(
                os.path.join(
                    settings.ONTASK_FIXTURE_DIR,
                    'survey_to_import.gz'),
                'rb'
        ) as file_obj:
            services.do_import_action(user, workflow=wflow, file_item=file_obj)

        Action.objects.get(name='Initial survey')


class EmailActionDetectIncorrectEmail(
    WrongEmailFixture,
    OnTaskTestCase,
):
    """Test if incorrect email addresses are detected."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):
        wflow = Workflow.objects.get(name=self.wflow_name)
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
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue(
            'Incorrect email address ' in str(resp.content))
        self.assertTrue(
            'incorrectemail_com' in str(resp.content))


class EmailActionChecksOnlySelectedEmails(
    FilterCorrectEmailsFixture,
    OnTaskTestCase,
):
    """Test if incorrect email addresses filtered out are allowed."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):
        wflow = Workflow.objects.get(name=self.wflow_name)
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
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue(
            'Action scheduled for execution' in str(resp.content))
        self.assertTrue(
            'You may check the status in log number' in str(resp.content))
