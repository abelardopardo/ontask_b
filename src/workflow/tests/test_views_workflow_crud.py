# -*- coding: utf-8 -*-

"""Test the views for the workflow pages."""

import os
import test
from test.compare import compare_workflows

from django.conf import settings
from django.urls import reverse

from action.models import Action, Condition
from ontask import entity_prefix
from table.models import View
from workflow.models import Column, Workflow
from workflow.views import clone_workflow, flush
from workflow.views.workflow_crud import delete, update


class WorkflowTestViewWorkflowCrud(test.OnTaskTestCase):
    """Test workflow views."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        '..',
        'initial_workflow',
        'initial_workflow.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'BIOL1011'

    def test_workflow_update(self):
        """Update the name and description of the workflow."""

        # Update name and description
        resp = self.get_response(
            'workflow:update',
            update,
            {'wid': self.workflow.id},
            is_ajax=True)
        self.assertEqual(resp.status_code, 200)
        resp = self.get_response(
            'workflow:update',
            update,
            {'wid': self.workflow.id},
            method='POST',
            req_params={
                'name': self.workflow.name + '2',
                'description_text': 'description'},
            is_ajax=True)
        self.assertEqual(resp.status_code, 200)
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow_name + '2', self.workflow.name)
        self.assertEqual(self.workflow.description_text, 'description')

    def test_workflow_clone_and_delete(self):
        """Clone a workflow."""

        # Invoke the clone function
        resp = self.get_response(
            'workflow:clone',
            clone_workflow,
            {'wid': self.workflow.id},
            is_ajax=True)
        self.assertEqual(resp.status_code, 200)
        resp = self.get_response(
            'workflow:clone',
            clone_workflow,
            {'wid': self.workflow.id},
            method='POST',
            is_ajax=True)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(Workflow.objects.count(), 2)

        new_wf = Workflow.objects.get(
            name=entity_prefix() + self.workflow_name)
        compare_workflows(self.workflow, new_wf)

        # Flush the workflow
        resp = self.get_response(
            'workflow:flush',
            flush,
            {'wid': new_wf.id},
            is_ajax=True)
        self.assertEqual(resp.status_code, 200)
        resp = self.get_response(
            'workflow:flush',
            flush,
            {'wid': new_wf.id},
            method='POST',
            is_ajax=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(new_wf.has_table())
        self.assertEqual(Workflow.objects.count(), 2)
        self.assertEqual(
            Column.objects.count(),
            self.workflow.columns.count())
        self.assertEqual(
            Action.objects.count(),
            self.workflow.actions.count())
        self.assertTrue(all(
            cond.action.workflow == self.workflow
            for cond in Condition.objects.all())
        )
        self.assertEqual(
            View.objects.count(),
            self.workflow.views.count())

        # Delete the workflow
        resp = self.get_response(
            'workflow:delete',
            delete,
            {'wid': new_wf.id},
            is_ajax=True)
        self.assertEqual(resp.status_code, 200)
        resp = self.get_response(
            'workflow:delete',
            delete,
            {'wid': new_wf.id},
            method='POST',
            is_ajax=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Workflow.objects.count(), 1)
