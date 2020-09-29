# -*- coding: utf-8 -*-

"""Test the views for the workflow pages."""

from rest_framework import status

from ontask import entity_prefix, models, tests
from ontask.tests.compare import compare_workflows


class WorkflowCrudBasic(tests.OnTaskTestCase, tests.InitialWorkflowFixture):
    """Test workflow views."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'


class WorkflowCrudUpdate(WorkflowCrudBasic):
    """Test workflow update."""

    def test(self):
        """Update the name and description of the workflow."""
        # Update name and description
        resp = self.get_response(
            'workflow:update',
            {'wid': self.workflow.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.get_response(
            'workflow:update',
            {'wid': self.workflow.id},
            method='POST',
            req_params={
                'name': self.workflow.name + '2',
                'description_text': 'description'},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        self.workflow.refresh_from_db()
        self.assertEqual(self.wflow_name + '2', self.workflow.name)
        self.assertEqual(self.workflow.description_text, 'description')


class WorkflowCloneDelete(WorkflowCrudBasic):
    """Test workflow clone and delete."""

    def test(self):
        """Clone a workflow."""
        # Invoke the clone function
        resp = self.get_response(
            'workflow:clone',
            {'wid': self.workflow.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.get_response(
            'workflow:clone',
            {'wid': self.workflow.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        self.assertEqual(models.Workflow.objects.count(), 2)

        new_wf = models.Workflow.objects.get(
            name=entity_prefix() + self.wflow_name)
        compare_workflows(self.workflow, new_wf)

        # Flush the workflow
        resp = self.get_response(
            'workflow:flush',
            {'wid': new_wf.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.get_response(
            'workflow:flush',
            {'wid': new_wf.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertFalse(new_wf.has_table())
        self.assertEqual(models.Workflow.objects.count(), 2)
        self.assertEqual(
            models.Column.objects.count(),
            self.workflow.columns.count())
        self.assertEqual(
            models.Action.objects.count(),
            self.workflow.actions.count())
        self.assertTrue(all(
            cond.action.workflow == self.workflow
            for cond in models.Condition.objects.all()))
        self.assertEqual(
            models.View.objects.count(),
            self.workflow.views.count())

        # Delete the workflow
        resp = self.get_response(
            'workflow:delete',
            {'wid': new_wf.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.get_response(
            'workflow:delete',
            {'wid': new_wf.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(models.Workflow.objects.count(), 1)


class WorkflowCrudAssignLUser(WorkflowCrudBasic):
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
