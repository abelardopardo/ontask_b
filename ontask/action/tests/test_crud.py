# -*- coding: utf-8 -*-

"""Test action CRUD functions."""
from rest_framework import status

from ontask import models, tests


class ActionViewCRUDBasic(tests.InitialWorkflowFixture, tests.OnTaskTestCase):
    """Basic class to test action CRUD views."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'


class ActionViewCRUDCreate(ActionViewCRUDBasic):
    """Test to create a new action."""

    def test(self):
        """Create a new action."""
        new_name = 'new action name'
        description = 'action description'

        actions_before = self.workflow.actions.count()

        resp = self.get_response('action:create', is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.get_response(
            'action:create',
            method='POST',
            req_params={
                'name': new_name,
                'description_text': description,
                'action_type': models.Action.PERSONALIZED_TEXT},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(actions_before + 1, self.workflow.actions.count())
        action = self.workflow.actions.get(name=new_name)
        self.assertEqual(action.name, new_name)
        self.assertEqual(action.description_text, description)


class ActionViewCRUDUpdate(ActionViewCRUDBasic):
    """Test the view to update a view."""

    def test(self):
        """Update the action."""
        action = self.workflow.actions.get(name='Midterm comments')
        old_name = action.name
        old_description = action.description_text

        resp = self.get_response(
            'action:update',
            url_params={'pk': action.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.get_response(
            'action:update',
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'name': action.name + '2',
                'description_text': action.description_text + '2',
                'action_type': action.action_type},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        action.refresh_from_db()
        self.assertEqual(action.name, old_name + '2')
        self.assertEqual(action.description_text, old_description + '2')


class ActionViewCRUDDelete(ActionViewCRUDBasic):
    """Test to delete an action."""

    def test(self):
        """Delete the action."""
        name = 'Midterm comments'
        action = self.workflow.actions.get(name=name)
        actions_before = self.workflow.actions.count()

        resp = self.get_response(
            'action:delete',
            url_params={'pk': action.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.get_response(
            'action:delete',
            url_params={'pk': action.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertFalse(self.workflow.actions.filter(name=name).exists())
        self.assertEqual(models.Action.objects.count() + 1, actions_before)


class ActionViewCRUDClone(ActionViewCRUDBasic):
    """Test the action clone view."""

    def test(self):
        """Clone the action."""
        name = 'Midterm comments'
        action = self.workflow.actions.get(name=name)
        actions_before = self.workflow.actions.count()
        filters_before = self.workflow.filters.count()

        resp = self.get_response(
            'action:clone',
            url_params={'pk': action.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        resp = self.get_response(
            'action:clone',
            url_params={'pk': action.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue(
            self.workflow.actions.filter(name='Copy of ' + name).exists())
        self.assertEqual(models.Action.objects.count(), actions_before + 1)
        self.assertEqual(models.Filter.objects.count(), filters_before + 1)
