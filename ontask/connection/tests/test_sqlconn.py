# -*- coding: utf-8 -*-

"""Test views to manipulate the SQL connections."""
import os

from django.conf import settings
from django.urls import reverse
from rest_framework import status

from ontask import models, tests


class DataopsSQLConnectionsBasic(tests.OnTaskTestCase):
    """Test the SQL connection views."""

    fixtures = ['empty_wflow']

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'wflow1'


class DataopsViewSQLConnections(DataopsSQLConnectionsBasic):
    """Test the SQL connection views."""

    def test(self):
        """Test the view to filter items."""
        resp = self.get_response('connection:sqlconns_index')
        self.assertTrue(status.is_success(resp.status_code))


class DataopsViewSQLConnectionsAdmin(DataopsSQLConnectionsBasic):
    """Test the SQL connection views."""

    user_email = 'superuser@bogus.com'

    def test(self):
        """Test the view to filter items."""
        resp = self.get_response('connection:sqlconns_admin_index')
        self.assertTrue(status.is_success(resp.status_code))

        # Add a new connection (GET)
        resp = self.get_response('connection:sqlconn_add', is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        # Add a new connection (POST)
        resp = self.get_response(
            'connection:sqlconn_add',
            method='POST',
            req_params={
                'name': 'conn name',
                'conn_type': 'postgresql',
                'db_name': 'DB NAME',
                'db_table': 'TABLE NAME'},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Object in db
        sqlconn = models.SQLConnection.objects.get(name='conn name')
        self.assertEqual(models.SQLConnection.objects.count(), 1)
        self.assertEqual(sqlconn.conn_type, 'postgresql')
        self.assertEqual(sqlconn.db_name, 'DB NAME')
        self.assertEqual(sqlconn.db_table, 'TABLE NAME')

        # Request to view
        resp = self.get_response(
            'connection:sqlconn_view',
            {'pk': sqlconn.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Request to edit (GET)
        resp = self.get_response(
            'connection:sqlconn_edit',
            {'pk': sqlconn.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        # Edit a connection (POST)
        resp = self.get_response(
            'connection:sqlconn_edit',
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
        sqlconn = models.SQLConnection.objects.get(name='conn name2')
        self.assertEqual(models.SQLConnection.objects.count(), 1)
        self.assertEqual(sqlconn.conn_type, 'postgresql')
        self.assertEqual(sqlconn.db_name, 'DB NAME2')
        self.assertEqual(sqlconn.db_table, 'TABLE NAME2')

        # Clone get
        resp = self.get_response(
            'connection:sqlconn_clone',
            {'pk': sqlconn.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        # Clone post
        resp = self.get_response(
            'connection:sqlconn_clone',
            {'pk': sqlconn.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Object in db
        sqlconn = models.SQLConnection.objects.get(name='Copy of conn name2')
        self.assertEqual(models.SQLConnection.objects.count(), 2)
        self.assertEqual(sqlconn.conn_type, 'postgresql')
        self.assertEqual(sqlconn.db_name, 'DB NAME2')
        self.assertEqual(sqlconn.db_table, 'TABLE NAME2')

        # Delete get
        resp = self.get_response(
            'connection:sqlconn_delete',
            {'pk': sqlconn.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        # Delete post
        resp = self.get_response(
            'connection:sqlconn_delete',
            {'pk': sqlconn.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Object in db
        self.assertEqual(models.SQLConnection.objects.count(), 1)


class DataopsRunSQLConnections(tests.OnTaskTestCase):
    """Test the SQL connection run."""

    fixtures = ['ontask/tests/initial_workflow/initial_workflow.json']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'tests',
        'initial_workflow',
        'initial_workflow.sql'
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'BIOL1011'

    def test(self):
        """Execute the RUN step."""

        sql_conn = models.SQLConnection.objects.get(pk=1)
        self.assertIsNotNone(sql_conn)

        # Modify the item so that it is able to access the DB
        sql_conn.conn_type = 'postgresql'
        sql_conn.db_name = settings.DATABASE_URL['NAME']
        sql_conn.db_user = settings.DATABASE_URL['USER']
        sql_conn.db_password = settings.DATABASE_URL['PASSWORD']
        sql_conn.db_port = settings.DATABASE_URL['PORT']
        sql_conn.db_host = settings.DATABASE_URL['HOST']
        sql_conn.db_table = '__ONTASK_WORKFLOW_TABLE_1'
        sql_conn.save()

        # Load the first step for the sql upload form (GET)
        resp = self.get_response(
            'dataops:sqlupload_start',
            {'pk': sql_conn.id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertIn('Establish a SQL connection', str(resp.content))

        # Load the first step for the sql upload form (POST)
        resp = self.get_response(
            'dataops:sqlupload_start',
            {'pk': sql_conn.id},
            method='POST',
            req_params={'db_password': 'boguspwd'})
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.url, reverse('dataops:upload_s2'))
