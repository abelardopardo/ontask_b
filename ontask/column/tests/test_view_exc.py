# -*- coding: utf-8 -*-

"""Test error generation when handling columns."""

from django.contrib import messages
from django.db import connection
from psycopg2 import sql

from ontask import tests


class ColumnCreate(tests.OnTaskTestCase, tests.EmptyWorkflowFixture):
    """Test column views."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

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


class ColumnCrudCreatePostError(
    tests.OnTaskTestCase,
    tests.SimpleWorkflowFixture
):
    """Test Exceptions when creating columns"""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

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
