# -*- coding: utf-8 -*-

"""Test the views for the column pages."""
from django.urls import reverse
from rest_framework import status

from ontask import models, tests
from ontask.dataops import pandas


class ColumnCriterionCrudBasic(
    tests.InitialWorkflowFixture,
    tests.OnTaskTestCase
):
    """Test criterion crud views."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'


class ColumnRemoveCriteria(ColumnCriterionCrudBasic):
    """Test rubric cells are deleted after removing criterion."""

    def test(self):
        criterion_name = 'Structure'
        action_name = 'Project feedback'

        # Get the three elements, action, column, and criteria.
        action = self.workflow.actions.get(name=action_name)

        criteria = action.column_condition_pair
        self.assertEqual(criteria.count(), 2)

        cc_tuple = criteria.get(column__name=criterion_name)
        criterion = cc_tuple.column

        # Get the rubric cells attached to the criteria
        rubric_cells = action.rubric_cells.filter(column=criterion)

        # Assert that the criteria has three rubric cells attached to it
        self.assertEqual(rubric_cells.count(), 3)

        # Delete the criterion
        resp = self.get_response(
            'column:criterion_delete',
            {'pk': cc_tuple.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Assert that the criteria has three rubric cells attached to it
        self.assertEqual(
            action.rubric_cells.filter(column=criterion).count(),
            0)

        # Get the edit page and verify that criteria is available for insertion
        resp = self.get_response('action:edit', {'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertIn('Insert existing criterion/column', str(resp.content))
        self.assertIn(
            reverse(
                'column:criterion_insert',
                kwargs={'pk': action.id, 'cpk': criterion.id}),
            str(resp.content))

        # Add the same criterion again
        resp = self.get_response(
            'column:criterion_insert',
            {'pk': action.id, 'cpk': criterion.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Assert that the criteria has three rubric cells attached to it
        self.assertEqual(
            action.rubric_cells.filter(column=criterion).count(),
            0)


class ColumnModifyCategoryRubric(ColumnCriterionCrudBasic):
    """Test modifying column categories in rubric is not allowed."""

    def test(self):
        criterion_name = 'Structure'

        # Get the column to modify
        column = self.workflow.columns.get(name=criterion_name)

        # Create the new question
        resp = self.get_response(
            'column:column_edit',
            {'pk': column.id},
            method='POST',
            req_params={
                'name': column.name,
                'description_text': column.description_text,
                'data_type': column.data_type,
                'position': '0',
                'raw_categories': ', '.join(column.categories) + ', Another'},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        self.assertIn(
            'Changes not allowed. Column is part of rubric action',
            str(resp.content))
