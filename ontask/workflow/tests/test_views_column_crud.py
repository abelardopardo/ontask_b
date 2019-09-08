# -*- coding: utf-8 -*-

"""Test the views for the column pages."""

import os
import test

from django.conf import settings
from rest_framework import status

from ontask.dataops.pandas import load_table
from ontask.models import Action


class WorkflowTestViewColumnCrud(test.OnTaskTestCase):
    """Test column views."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'test',
        'initial_workflow',
        'initial_workflow.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'BIOL1011'

    def test_column_add(self):
        """Add a column."""
        column_name = 'cname'
        column_description = 'column description'
        column_categories = '   a,b,c,d   '

        # Adding a new column of type integer
        resp = self.get_response('workflow:column_add', is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.get_response(
            'workflow:column_add',
            method='POST',
            req_params={
                'name': column_name,
                'description_text': column_description,
                'data_type': 'string',
                'position': '0',
                'raw_categories': column_categories},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        self.workflow.refresh_from_db()
        new_col = self.workflow.columns.get(name=column_name)
        self.assertEqual(new_col.description_text, column_description)
        self.assertEqual(new_col.data_type, 'string')
        self.assertEqual(
            len(new_col.categories),
            len([txt.strip() for txt in column_categories.split(',')]))

    def test_question_add(self):
        """Test adding a question to a survey."""
        # Get the survey action
        survey = self.workflow.actions.get(action_type=Action.SURVEY)

        # GET the form
        resp = self.get_response(
            'workflow:question_add',
            {'pk': survey.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Create the new question
        resp = self.get_response(
            'workflow:question_add',
            {'pk': survey.id},
            method='POST',
            req_params={
                'name': 'NEW QUESTION',
                'description_text': 'QUESTION DESCRIPTION',
                'data_type': 'string',
                'position': '0',
                'raw_categories': 'A,B,C,D'},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

    def test_question_rename(self):
        """Test renaming a question in a survey."""
        # Get the survey action and the first of the columns
        survey = self.workflow.actions.get(action_type=Action.SURVEY)
        column = survey.column_condition_pair.first().column
        old_name = column.name
        # GET the form
        resp = self.get_response(
            'workflow:question_edit',
            {'pk': column.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Create the new question
        resp = self.get_response(
            'workflow:question_edit',
            {'pk': column.id},
            method='POST',
            req_params={
                'name': column.name + '2',
                'description_text': column.description_text,
                'data_type': column.data_type,
                'position': column.position,
                'raw_categories': column.categories},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        column.refresh_from_db()
        self.assertEqual(column.name, old_name + '2')

    def test_formula_column_add(self):
        """Test adding a formula column."""
        # GET the form
        resp = self.get_response('workflow:formula_column_add', is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Create the new question
        resp = self.get_response(
            'workflow:formula_column_add',
            method='POST',
            req_params={
                'name': 'FORMULA COLUMN',
                'description_text': 'FORMULA COLUMN DESC',
                'data_type': 'integer',
                'position': '0',
                'columns': ['12', '13'],
                'op_type': 'sum'},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        df = load_table(self.workflow.get_data_frame_table_name())
        self.assertTrue(
            df['FORMULA COLUMN'].equals(df['Q01'] + df['Q02']))

    def test_random_column_add(self):
        """Test adding a random column."""
        # GET the form
        resp = self.get_response('workflow:random_column_add', is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Create the new question
        resp = self.get_response(
            'workflow:random_column_add',
            method='POST',
            req_params={
                'name': 'RANDOM COLUMN',
                'description_text': 'RANDOM COLUMN DESC',
                'data_type': 'integer',
                'position': '0',
                'column_values': '12'},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        df = load_table(self.workflow.get_data_frame_table_name())
        self.assertTrue(all(0 < num < 13 for num in df['RANDOM COLUMN']))

    def test_column_clone(self):
        """Test adding a random column."""
        column = self.workflow.columns.get(name='Q01')
        resp = self.get_response(
            'workflow:column_clone',
            {'pk': column.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Create the new question
        resp = self.get_response(
            'workflow:column_clone',
            {'pk': column.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        df = load_table(self.workflow.get_data_frame_table_name())
        self.assertTrue(df['Copy of Q01'].equals(df['Q01']))

    def test_column_restrict(self):
        """Test Column restriction."""
        column = self.workflow.columns.get(name='Gender')
        self.assertEqual(column.categories, [])

        resp = self.get_response(
            'workflow:column_restrict',
            {'pk': column.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        resp = self.get_response(
            'workflow:column_restrict',
            {'pk': column.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        column.refresh_from_db()
        self.assertEqual(set(column.categories), {'female', 'male'})

    def test_assign_luser_column(self):
        """Test assign luser column option."""
        column = self.workflow.columns.get(name='email')
        self.assertEqual(self.workflow.luser_email_column, None)

        resp = self.get_response(
            'workflow:assign_luser_column',
            {'pk': column.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        column = self.workflow.columns.get(name='email')
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.luser_email_column, column)
        self.assertEqual(self.workflow.lusers.count(), self.workflow.nrows)
