# -*- coding: utf-8 -*-

"""Test views to manipulate the SQL connections."""
import test

from rest_framework import status

from ontask.apps.dataops.models import SQLConnection


class DataopsViewSQLConnections(test.OnTaskTestCase):
    """Test the SQL connection views."""

    fixtures = ['empty_wflow']

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'wflow1'

    def test_sql_views_instructor(self):
        """Test the view to filter items."""
        resp = self.get_response('dataops:sqlconns_instructor_index')
        self.assertTrue(status.is_success(resp.status_code))


class DataopsViewSQLConnectionsAdmin(test.OnTaskTestCase):
    """Test the SQL connection views."""

    fixtures = ['empty_wflow']

    user_email = 'superuser@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'wflow1'

    def test_sql_views_admin(self):
        """Test the view to filter items."""
        resp = self.get_response('dataops:sqlconns_admin_index')
        self.assertTrue(status.is_success(resp.status_code))

        # Add a new connection (GET)
        resp = self.get_response('dataops:sqlconn_add', is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        # Add a new connection (POST)
        resp = self.get_response(
            'dataops:sqlconn_add',
            method='POST',
            req_params={
                'name': 'conn name',
                'conn_type': 'postgresql',
                'db_name': 'DB NAME',
                'db_table': 'TABLE NAME'},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Object in db
        sqlconn = SQLConnection.objects.get(name='conn name')
        self.assertEqual(SQLConnection.objects.count(), 1)
        self.assertEqual(sqlconn.conn_type, 'postgresql')
        self.assertEqual(sqlconn.db_name, 'DB NAME')
        self.assertEqual(sqlconn.db_table, 'TABLE NAME')

        # Request to view
        resp = self.get_response(
            'dataops:sqlconn_view',
            {'pk': sqlconn.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Request to edit (GET)
        resp = self.get_response(
            'dataops:sqlconn_edit',
            {'pk': sqlconn.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        # Edit a connection (POST)
        resp = self.get_response(
            'dataops:sqlconn_edit',
            {'pk': sqlconn.id},
            method='POST',
            req_params={
                'name': 'conn name2',
                'conn_type': 'postgresql',
                'db_name': 'DB NAME2',
                'db_table': 'TABLE NAME2'},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Object in db
        sqlconn = SQLConnection.objects.get(name='conn name2')
        self.assertEqual(SQLConnection.objects.count(), 1)
        self.assertEqual(sqlconn.conn_type, 'postgresql')
        self.assertEqual(sqlconn.db_name, 'DB NAME2')
        self.assertEqual(sqlconn.db_table, 'TABLE NAME2')

        # Clone get
        resp = self.get_response(
            'dataops:sqlconn_clone',
            {'pk': sqlconn.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        # Clone post
        resp = self.get_response(
            'dataops:sqlconn_clone',
            {'pk': sqlconn.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Object in db
        sqlconn = SQLConnection.objects.get(name='Copy of conn name2')
        self.assertEqual(SQLConnection.objects.count(), 2)
        self.assertEqual(sqlconn.conn_type, 'postgresql')
        self.assertEqual(sqlconn.db_name, 'DB NAME2')
        self.assertEqual(sqlconn.db_table, 'TABLE NAME2')

        # Delete get
        resp = self.get_response(
            'dataops:sqlconn_delete',
            {'pk': sqlconn.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        # Delete post
        resp = self.get_response(
            'dataops:sqlconn_delete',
            {'pk': sqlconn.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Object in db
        sqlconn = SQLConnection.objects.get(name='conn name2')
        self.assertEqual(SQLConnection.objects.count(), 1)
