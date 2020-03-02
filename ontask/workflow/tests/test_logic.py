# -*- coding: utf-8 -*-

"""Test workflow basic operations"""
import gzip
import json
import os
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_datetime
from django.utils.six import BytesIO
from rest_framework import status
from rest_framework.parsers import JSONParser

from ontask import models, tests
from ontask.dataops import pandas
from ontask.tests.compare import compare_workflows
from ontask.workflow import services


class WorkflowImportExport(tests.OnTaskTestCase):
    """Test import export functionality."""
    fixtures = ['simple_workflow_export']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'simple_workflow_export.sql'
    )

    def test_export(self):
        """Test the export functionality."""
        # Get the only workflow
        workflow = models.Workflow.objects.get(name='wflow1')

        # Export data only
        response = services.do_export_workflow(
            workflow,
            workflow.actions.all())

        self.assertEqual(response.get('Content-Type'),
            'application/octet-stream')
        self.assertEqual(response['Content-Transfer-Encoding'], 'binary')
        self.assertTrue(
            response.get('Content-Disposition').startswith(
                'attachment; filename="ontask_workflow'
            )
        )

        # Process the file
        data_in = gzip.GzipFile(fileobj=BytesIO(response.content))
        data = JSONParser().parse(data_in)

        # Compare the data with the current workflow
        self.assertEqual(workflow.actions.count(), len(data['actions']))
        self.assertEqual(workflow.nrows, data['nrows'])
        self.assertEqual(workflow.ncols, data['ncols'])
        self.assertEqual(workflow.attributes, data['attributes'])
        self.assertEqual(workflow.query_builder_ops, data['query_builder_ops'])


class WorkflowImportExportCycle(tests.OnTaskTestCase):
    fixtures = ['initial_db']

    gz_filename = os.path.join(
        settings.BASE_DIR(),
        'initial_workflow.gz')
    tmp_filename = os.path.join('tmp')

    wflow_name = 'initial workflow'
    wflow_name2 = 'initial workflow2'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.workflow = None

    def test_01_cycle(self):
        # Obtain user
        user = get_user_model().objects.filter(
            email='instructor01@bogus.com'
        ).first()

        # User must exist
        self.assertIsNotNone(user, 'User instructor01@bogus.com not found')

        # Workflow must not exist
        self.assertFalse(
            models.Workflow.objects.filter(
                user__email='instructor01@bogus.com',
                name=self.wflow_name
            ).exists(),
            'A workflow with this name already exists')

        with open(self.gz_filename, 'rb') as f:
            services.do_import_workflow_parse(user, self.wflow_name, f)

        # Get the new workflow
        workflow = models.Workflow.objects.filter(name=self.wflow_name).first()
        self.assertIsNotNone(workflow, 'Incorrect import operation')

        # Do the export now
        filename = os.path.join(tempfile.gettempdir(), 'ontask_tests.gz')
        zbuf = services.do_export_workflow_parse(
            workflow,
            workflow.actions.all())
        zbuf.seek(0)
        with open(filename, 'wb') as f:
            shutil.copyfileobj(zbuf, f, length=131072)

        # Import again!
        with open(filename, 'rb') as f:
            services.do_import_workflow_parse(user, self.wflow_name2, f)

        # Do the export now
        workflow2 = models.Workflow.objects.filter(
            name=self.wflow_name2).first()
        self.assertIsNotNone(workflow, 'Incorrect import operation')

        compare_workflows(workflow, workflow2)

        # Compare the workflows
        self.assertEqual(workflow.description_text, workflow2.description_text)
        self.assertEqual(workflow.nrows, workflow2.nrows)
        self.assertEqual(workflow.ncols, workflow2.ncols)
        self.assertEqual(workflow.attributes, workflow2.attributes)
        self.assertEqual(workflow.query_builder_ops,
            workflow2.query_builder_ops)

        columns1 = workflow.columns.all()
        columns2 = workflow2.columns.all()
        self.assertEqual(columns1.count(), columns2.count())
        for c1, c2 in zip(columns1, columns2):
            self.assertEqual(c1.name, c2.name)
            self.assertEqual(c1.description_text, c2.description_text)
            self.assertEqual(c1.data_type, c2.data_type)
            self.assertEqual(c1.is_key, c2.is_key)
            self.assertEqual(c1.position, c2.position)
            self.assertEqual(c1.categories, c2.categories)
            self.assertEqual(c1.active_from, c2.active_from)
            self.assertEqual(c1.active_to, c2.active_to)

        actions1 = workflow.actions.all()
        actions2 = workflow2.actions.all()
        self.assertEqual(actions1.count(), actions2.count())
        for a1, a2 in zip(actions1, actions2):
            self.assertEqual(a1.name, a2.name)
            self.assertEqual(a1.description_text, a2.description_text)
            self.assertEqual(a1.action_type, a2.action_type)
            self.assertEqual(a1.serve_enabled, a2.serve_enabled)
            self.assertEqual(a1.active_from, a2.active_from)
            self.assertEqual(a1.active_to, a2.active_to)
            self.assertEqual(a1.rows_all_false, a2.rows_all_false)
            self.assertEqual(a1.text_content, a2.text_content)
            self.assertEqual(a1.target_url, a2.target_url)
            self.assertEqual(a1.shuffle, a2.shuffle)

            conditions1 = a1.conditions.all()
            conditions2 = a2.conditions.all()
            self.assertEqual(conditions1.count(), conditions2.count())
            for c1, c2 in zip(conditions1, conditions2):
                self.assertEqual(c1.name, c2.name)
                self.assertEqual(c1.description_text, c2.description_text)
                self.assertEqual(c1.formula, c2.formula)
                self.assertEqual(c1.columns.count(), c2.columns.count())
                self.assertEqual(c1.n_rows_selected, c2.n_rows_selected)
                self.assertEqual(c1.is_filter, c2.is_filter)

                cl1 = c1.columns.all()
                cl2 = c2.columns.all()
                self.assertEqual(cl1.count(), cl2.count())
                for x1, x2 in zip(cl1, cl2):
                    self.assertEqual(x1.name, x2.name)

            tuple1 = a1.column_condition_pair.all()
            tuple2 = a2.column_condition_pair.all()
            self.assertEqual(tuple1.count(), tuple2.count())
            for titem1, titem2 in zip(tuple1, tuple2):
                self.assertEqual(titem1.action.name, titem2.action.name)
                self.assertEqual(titem1.column.name, titem2.column.name)
                if titem1.condition:
                    self.assertEqual(
                        titem1.condition.name,
                        titem2.condition.name)


class WorkflowDelete(tests.OnTaskTestCase):
    fixtures = ['test_merge']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'test_merge.sql'
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def test_delete(self):
        """Test invokation of delete table"""
        # Get the workflow first
        self.workflow = models.Workflow.objects.all().first()

        # JSON POST request for workflow delete
        resp = self.get_response(
            'workflow:delete',
            method='POST',
            url_params={'wid': self.workflow.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue(models.Workflow.objects.count() == 0)
        self.workflow = None


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
