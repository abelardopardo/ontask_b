# -*- coding: utf-8 -*-

"""Test column basic operations"""
import json
import os

from django.conf import settings
from django.utils.dateparse import parse_datetime
from rest_framework import status

from ontask import models, tests
from ontask.dataops import pandas
from ontask.workflow import services


class ColumnAddRandomColumnForm(tests.OnTaskTestCase):
    """Test the creation of random columns."""

    fixtures = ['simple_table']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'simple_table.sql'
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'wflow1'

    def test_create_random_column_number_form(self):
        """Create a random number column with no values"""
        # Get the workflow first
        self.workflow = models.Workflow.objects.all().first()

        # Column name and current number of them
        cname = 'random_column'
        ncols = self.workflow.ncols

        # JSON POST request for column creation with string value
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': cname,
                'data_type': 'double',
                'raw_categories': 'bogus',
                'position': 0},
            is_ajax=True)

        resp_content = json.loads(resp.content)
        self.assertTrue('html_form' in resp_content)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.ncols, ncols)
        new_column = self.workflow.columns.filter(name=cname).first()
        self.assertIsNone(new_column)

        # JSON POST request for column creation with a single integer
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': cname,
                'data_type': 'double',
                'raw_categories': '13.0',
                'position': 0},
            is_ajax=True)

        resp_content = json.loads(resp.content)
        self.assertTrue('html_form' in resp_content)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.ncols, ncols)
        new_column = self.workflow.columns.filter(name=cname).first()
        self.assertIsNone(new_column)

        # JSON POST request for column creation with a multiple strings
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': cname,
                'data_type': 'double',
                'raw_categories': 'one, two, three',
                'position': 0},
            is_ajax=True)

        resp_content = json.loads(resp.content)
        self.assertTrue('html_form' in resp_content)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.ncols, ncols)
        new_column = self.workflow.columns.filter(name=cname).first()
        self.assertIsNone(new_column)

        # JSON POST request for column creation with a interval integer
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': cname,
                'data_type': 'double',
                'raw_categories': '-3.0 - -5.0',
                'position': 0},
            is_ajax=True)

        resp_content = json.loads(resp.content)
        self.assertTrue('html_form' not in resp_content)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.ncols, ncols + 1)
        new_column = self.workflow.columns.filter(name=cname).first()
        self.assertIsNotNone(new_column)
        self.assertEqual(new_column.name, cname)
        self.assertEqual(new_column.data_type, 'double')
        data_frame = pandas.load_table(
            self.workflow.get_data_frame_table_name())
        self.assertTrue(all(
            element in [-3, -4, -5] for element in data_frame[cname]))
        # Delete the column
        services.delete_column(self.workflow.user, self.workflow, new_column)

        # JSON POST request for column creation with an integer list
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': cname,
                'data_type': 'double',
                'raw_categories': '17, 18, 19',
                'position': 0},
            is_ajax=True)

        resp_content = json.loads(resp.content)
        self.assertTrue('html_form' not in resp_content)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.ncols, ncols + 1)
        new_column = self.workflow.columns.filter(name=cname).first()
        self.assertIsNotNone(new_column)
        self.assertEqual(new_column.name, cname)
        self.assertEqual(new_column.data_type, 'double')
        data_frame = pandas.load_table(
            self.workflow.get_data_frame_table_name())
        self.assertTrue(all(
            element in [17, 18, 19] for element in data_frame[cname]))

    def test_create_random_column_string_form(self):
        """Create a random string column"""
        # Get the workflow first
        self.workflow = models.Workflow.objects.all().first()

        # Column name and current number of them
        cname = 'random_column'
        ncols = self.workflow.ncols

        # JSON POST request for column creation with string value
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': cname,
                'data_type': 'string',
                'raw_categories': 'bogus',
                'position': 0},
            is_ajax=True)

        resp_content = json.loads(resp.content)
        self.assertTrue('html_form' in resp_content)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.ncols, ncols)
        new_column = self.workflow.columns.filter(name=cname).first()
        self.assertIsNone(new_column)

        # JSON POST request for column creation with a string list
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': cname,
                'data_type': 'string',
                'raw_categories': 'one, two, three',
                'position': 0},
            is_ajax=True)

        resp_content = json.loads(resp.content)
        self.assertTrue('html_form' not in resp_content)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.ncols, ncols + 1)
        new_column = self.workflow.columns.filter(name=cname).first()
        self.assertIsNotNone(new_column)
        self.assertEqual(new_column.name, cname)
        self.assertEqual(new_column.data_type, 'string')
        data_frame = pandas.load_table(
            self.workflow.get_data_frame_table_name())
        self.assertTrue(all(
            element in ['one', 'two', 'three']
            for element in data_frame[cname]))

    def test_create_random_column_boolean_form(self):
        """Create a random string column"""
        # Get the workflow first
        self.workflow = models.Workflow.objects.all().first()

        # Column name and current number of them
        cname = 'random_column'
        ncols = self.workflow.ncols

        # JSON POST request for column creation with string value
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': cname,
                'data_type': 'boolean',
                'raw_categories': 'bogus',
                'position': 0},
            is_ajax=True)

        resp_content = json.loads(resp.content)
        self.assertTrue('html_form' in resp_content)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.ncols, ncols)
        new_column = self.workflow.columns.filter(name=cname).first()
        self.assertIsNone(new_column)

        # JSON POST request for column creation with string value
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': cname,
                'data_type': 'boolean',
                'raw_categories': 'one, two',
                'position': 0},
            is_ajax=True)

        resp_content = json.loads(resp.content)
        self.assertTrue('html_form' not in resp_content)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.ncols, ncols + 1)
        new_column = self.workflow.columns.filter(name=cname).first()
        self.assertIsNotNone(new_column)
        self.assertEqual(new_column.name, cname)
        self.assertEqual(new_column.data_type, 'boolean')
        data_frame = pandas.load_table(
            self.workflow.get_data_frame_table_name())
        self.assertTrue(all(not element for element in data_frame[cname]))
        # Delete the column
        services.delete_column(self.workflow.user, self.workflow, new_column)

        # JSON POST request for column creation with a string list
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': cname,
                'data_type': 'boolean',
                'raw_categories': 'True, False',
                'position': 0},
            is_ajax=True)

        resp_content = json.loads(resp.content)
        self.assertTrue('html_form' not in resp_content)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.ncols, ncols + 1)
        new_column = self.workflow.columns.filter(name=cname).first()
        self.assertIsNotNone(new_column)
        self.assertEqual(new_column.name, cname)
        self.assertEqual(new_column.data_type, 'boolean')
        data_frame = pandas.load_table(
            self.workflow.get_data_frame_table_name())
        self.assertTrue(all(
            element in [True, False] for element in data_frame[cname]))

    def test_create_random_column_datetime_form(self):
        """Create a random number column with no values"""
        # Get the workflow first
        self.workflow = models.Workflow.objects.all().first()

        # Column name and current number of them
        cname = 'random_column'
        ncols = self.workflow.ncols

        # JSON POST request for column creation with incorrect string value
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': cname,
                'data_type': 'datetime',
                'raw_categories': 'bogus',
                'position': 0},
            is_ajax=True)

        resp_content = json.loads(resp.content)
        self.assertTrue('html_form' in resp_content)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.ncols, ncols)
        new_column = self.workflow.columns.filter(name=cname).first()
        self.assertIsNone(new_column)

        # JSON POST request for column creation with a single integer
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': cname,
                'data_type': 'datetime',
                'raw_categories': '2020-09-11 12:04:43+0930',
                'position': 0},
            is_ajax=True)

        resp_content = json.loads(resp.content)
        self.assertTrue('html_form' in resp_content)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.ncols, ncols)
        new_column = self.workflow.columns.filter(name=cname).first()
        self.assertIsNone(new_column)

        # JSON POST request for column creation with a multiple strings
        dtimes = [
            parse_datetime('2020-09-11 12:04:43+0930'),
            parse_datetime('2020-09-12 12:04:43+0930')]
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': cname,
                'data_type': 'datetime',
                'raw_categories':
                    '2020-09-11 12:04:43+0930, 2020-09-12 12:04:43+0930',
                'position': 0},
            is_ajax=True)

        resp_content = json.loads(resp.content)
        self.assertTrue('html_form' not in resp_content)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.ncols, ncols + 1)
        new_column = self.workflow.columns.filter(name=cname).first()
        self.assertIsNotNone(new_column)
        self.assertEqual(new_column.name, cname)
        self.assertEqual(new_column.data_type, 'datetime')
        data_frame = pandas.load_table(
            self.workflow.get_data_frame_table_name())
        self.assertTrue(all(
            element in dtimes for element in data_frame[cname]))
        # Delete the column
        services.delete_column(self.workflow.user, self.workflow, new_column)
