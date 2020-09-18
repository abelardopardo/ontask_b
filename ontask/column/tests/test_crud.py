# -*- coding: utf-8 -*-

"""Test the views for the column pages."""
import os

from django.conf import settings
from rest_framework import status

from ontask import models, tests
from ontask.dataops import pandas


class WorkflowTestViewColumnCrudBasic(tests.OnTaskTestCase):
    """Test column views."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'tests',
        'initial_workflow',
        'initial_workflow.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'BIOL1011'


class WorkflowTestViewColumnCreate(WorkflowTestViewColumnCrudBasic):
    """Test column views."""

    def test(self):
        """Add a column."""
        column_name = 'cname'
        column_description = 'column description'
        column_categories = '   a,b,c,d   '

        # Adding a new column of type integer
        resp = self.get_response('column:create', is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.get_response(
            'column:create',
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


class WorkflowTestViewQuestionAdd(WorkflowTestViewColumnCrudBasic):
    """Test Question Add."""

    def test_question_add(self):
        """Test adding a question to a survey."""
        # Get the survey action
        survey = self.workflow.actions.get(action_type=models.Action.SURVEY)

        # GET the form
        resp = self.get_response(
            'column:question_add',
            {'pk': survey.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Create the new question
        resp = self.get_response(
            'column:question_add',
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


class WorkflowTestViewQuestionRename(WorkflowTestViewColumnCrudBasic):
    """Test Question Rename."""

    def test(self):
        """Test renaming a question in a survey."""
        # Get the survey action and the first of the columns
        survey = self.workflow.actions.get(action_type=models.Action.SURVEY)
        column = survey.column_condition_pair.first().column
        old_name = column.name
        # GET the form
        resp = self.get_response(
            'column:question_edit',
            {'pk': column.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Create the new question
        resp = self.get_response(
            'column:question_edit',
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


class WorkflowTestViewAddFormulaColumn(WorkflowTestViewColumnCrudBasic):
    """Test adding a new column with a formula."""

    def test(self):
        """Test adding a formula column."""
        # GET the form
        resp = self.get_response('column:formula_column_add', is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Create the new question
        resp = self.get_response(
            'column:formula_column_add',
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

        df = pandas.load_table(self.workflow.get_data_frame_table_name())
        self.assertTrue(
            df['FORMULA COLUMN'].equals(df['Q01'] + df['Q02']))


class WorkflowTestViewAddRandomColumn(WorkflowTestViewColumnCrudBasic):
    """Test adding a random colum."""

    def test(self):
        """Test adding a random column."""
        # GET the form
        resp = self.get_response('column:random_column_add', is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Create the new question
        resp = self.get_response(
            'column:random_column_add',
            method='POST',
            req_params={
                'name': 'RANDOM COLUMN',
                'description_text': 'RANDOM COLUMN DESC',
                'data_type': 'integer',
                'position': '0',
                'raw_categories': '1 - 12'},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        df = pandas.load_table(self.workflow.get_data_frame_table_name())
        self.assertTrue(all(0 < num < 13 for num in df['RANDOM COLUMN']))


class WorkflowTestViewCloneColumn(WorkflowTestViewColumnCrudBasic):
    """Test cloning a column."""

    def test(self):
        """Test adding a random column."""
        column = self.workflow.columns.get(name='Q01')
        resp = self.get_response(
            'column:column_clone',
            {'pk': column.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Create the new question
        resp = self.get_response(
            'column:column_clone',
            {'pk': column.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        df = pandas.load_table(self.workflow.get_data_frame_table_name())
        self.assertTrue(df['Copy of Q01'].equals(df['Q01']))


class WorkflowTestViewRestrictColumn(WorkflowTestViewColumnCrudBasic):
    """Test restricting values in a column."""

    def test(self):
        """Test Column restriction."""
        column = self.workflow.columns.get(name='Gender')
        self.assertEqual(column.categories, [])

        resp = self.get_response(
            'column:column_restrict',
            {'pk': column.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        resp = self.get_response(
            'column:column_restrict',
            {'pk': column.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        column.refresh_from_db()
        self.assertEqual(set(column.categories), {'female', 'male'})


class WorkflowTestViewAssignLUser(WorkflowTestViewColumnCrudBasic):
    """Test assign luser view."""

    def test(self):
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
