"""Test condition basic operations."""
from rest_framework import status

from ontask import models, tests


class ConditionTestSetFilterRowsSelected(
    tests.InitialWorkflowFixture,
    tests.OnTaskTestCase,
):
    """Test the creation of random columns."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):
        # Get the workflow
        self.workflow = models.Workflow.objects.all()[0]

        # Get the action
        action = self.workflow.actions.get(name='Midterm comments')

        # Get the view to use as filter
        view = self.workflow.views.get(name='Midterm')

        # Request to edit the action and verify that no warning is present
        resp = self.get_response('action:edit', url_params={'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertNotIn(
            'users have all conditions equal to FALSE',
            str(resp.content))

        # Delete the filter
        resp = self.get_response(
            'condition:delete_filter',
            url_params={'pk': action.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Request to edit the action and verify that the warning is present
        resp = self.get_response('action:edit', url_params={'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertIn(
            'users have all conditions equal to FALSE',
            str(resp.content))

        # Set the view as filter
        resp = self.get_response(
            'condition:set_filter',
            url_params={'pk': action.id, 'view_id': view.id},
            method='GET',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Request to edit the action and verify that no warning is present
        resp = self.get_response('action:edit', url_params={'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertNotIn(
            'users have all conditions equal to FALSE',
            str(resp.content))
