# -*- coding: utf-8 -*-

"""Test the views for the workflow pages."""

from rest_framework import status

from ontask import entity_prefix, models, tests
from ontask.tests.compare import compare_workflows


class WorkflowCrudBasic(tests.InitialWorkflowFixture, tests.OnTaskTestCase):
    """Test workflow views."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'


class WorkflowCrudCreate(WorkflowCrudBasic):
    """Test workflow create."""

    def test(self):
        """Create a workflow giving name and description."""
        new_name = self.workflow.name + '2'
        description = 'description'

        resp = self.get_response('workflow:create', is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.get_response(
            'workflow:create',
            method='POST',
            req_params={
                'name': new_name,
                'description_text': description},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue(models.Workflow.objects.all().count() == 2)
        new_wflow = models.Workflow.objects.get(name=new_name)
        self.assertEqual(new_wflow.name, new_name)
        self.assertEqual(new_wflow.description_text, description)


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
        self.assertFalse(new_wf.has_data_frame())
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
        self.assertEqual(
            models.Filter.objects.count(),
            self.workflow.filters.count())

        # Clone the empty workflow now
        resp = self.get_response(
            'workflow:clone',
            {'wid': new_wf.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.get_response(
            'workflow:clone',
            {'wid': new_wf.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        self.assertEqual(models.Workflow.objects.count(), 3)

        new_wf.refresh_from_db()
        new_wf2 = models.Workflow.objects.get(
            name=entity_prefix() + (entity_prefix() + self.wflow_name))
        compare_workflows(new_wf, new_wf2)

        # Delete the first cloned workflow
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
        self.assertEqual(models.Workflow.objects.count(), 2)

        # Delete the second cloned workflow
        resp = self.get_response(
            'workflow:delete',
            {'wid': new_wf2.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.get_response(
            'workflow:delete',
            {'wid': new_wf2.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(models.Workflow.objects.count(), 1)


class WorkflowCrudAssignLUser(WorkflowCrudBasic):
    """Test assign luser view."""

    def test(self):
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
