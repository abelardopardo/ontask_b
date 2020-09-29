# -*- coding: utf-8 -*-

"""Test error generation when handling columns."""
import os

from django.db import connection
from django.conf import settings
from django.contrib import messages
from psycopg2 import sql

from ontask import tests


class ColumnCrudEmptyWflow(tests.OnTaskTestCase):
    """Test Exceptions when creating views"""

    fixtures = ['empty_wflow']

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'wflow1'


class ColumnCreate(ColumnCrudEmptyWflow):
    """Test column views."""

    def test(self):
        """Add a column."""
        # Get the visualization for the whole table

        resp = self.get_response('column:create', is_ajax=True)
        self.assertIn('{"html_redirect": ""}', str(resp.content))

        msgs = list(messages.get_messages(self.last_request))
        self.assertEqual(len(msgs), 1)
        self.assertIn(
            'Cannot add column to a workflow without data',
            str(msgs[0]))


class ColumnCrudCreatePostError(tests.OnTaskTestCase):
    """Test Exceptions when creating columns"""

    fixtures = ['simple_workflow']
    filename = os.path.join(
        settings.ONTASK_FIXTURE_DIR,
        'simple_workflow.sql')

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'wflow1'

    def test(self):
        """Try to create a column when the DB returns an error."""

        # Inject a table rename to make the next request fail
        connection.connection.cursor().execute(
            sql.SQL('ALTER TABLE {0} RENAME TO {1}').format(
                sql.Identifier(self.workflow.data_frame_table_name),
                sql.Identifier('TEMPORARY_TABLE_NAME')))

        resp = self.get_response(
            'column:create',
            method='POST',
            req_params={
                'name': 'column name',
                'data_type': 'integer',
                'position': 0},
            is_ajax=True)
        self.assertIn('{"html_redirect": ""}', str(resp.content))
        msgs = list(messages.get_messages(self.last_request))
        self.assertEqual(len(msgs), 1)
        self.assertIn(
            'Unable to add element: relation "__ONTASK_WORKFLOW_TABLE_1" '
            'does not exist\n',
            str(msgs[0]))

        # Restore table structure to finish correctly
        connection.connection.cursor().execute(
            sql.SQL('ALTER TABLE {0} RENAME TO {1}').format(
                sql.Identifier('TEMPORARY_TABLE_NAME'),
                sql.Identifier(self.workflow.data_frame_table_name)))

