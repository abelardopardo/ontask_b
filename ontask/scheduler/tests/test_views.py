# -*- coding: utf-8 -*-

"""Test the views for the scheduler pages."""

import os
import test

from django.conf import settings
from rest_framework import status

from ontask.models import ScheduledAction


class SchedulerForms(test.OnTaskTestCase):
    """Test schedule creation through forms."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    fixtures = ['three_actions']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'three_actions.sql',
    )

    workflow_name = 'wflow1'

    s_name = 'Scheduling first JSON'
    s_desc = 'First JSON intervention'
    s_execute = '2119-05-03 12:32:18+10:30'

    def test_views_email(self):
        """Test the use of forms in to schedule actions."""
        # Index of all scheduled actions
        resp = self.get_response('scheduler:index')
        self.assertTrue(status.is_success(resp.status_code))

        # Get the email action object
        action = self.workflow.actions.get(name='simple action')

        # Get the form to schedule this action
        resp = self.get_response('scheduler:create', {'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))

        # POST the form to schedule this action
        resp = self.get_response(
            'scheduler:create',
            {'pk': action.id},
            method='POST',
            req_params={
                'name': 'First scheduling round',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'execute': '05/31/2119 14:35',
                'subject': 'Subject text',
            })
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(ScheduledAction.objects.count(), 1)

        # Change the name of the scheduled item
        sc_item = ScheduledAction.objects.first()
        resp = self.get_response(
            'scheduler:edit',
            {'pk': sc_item.id},
            method='POST',
            req_params={
                'name': 'First scheduling round2',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'execute': '05/31/2119 14:35',
                'subject': 'Subject text',
            })
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(ScheduledAction.objects.count(), 1)
        sc_item.refresh_from_db()

        self.assertEqual(sc_item.name, 'First scheduling round2')

        # Select the confirm items
        sc_item = ScheduledAction.objects.first()
        resp = self.get_response(
            'scheduler:edit',
            {'pk': sc_item.id},
            method='POST',
            req_params={
                'name': 'First scheduling round3',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'confirm_items': True,
                'execute': '05/31/2119 14:35',
                'subject': 'Subject text',
            })
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(ScheduledAction.objects.count(), 1)

        # Index of all scheduled actions (to execute the table render)
        resp = self.get_response('scheduler:index')
        self.assertTrue(status.is_success(resp.status_code))

        # View the information with a JSON request
        resp = self.get_response(
            'scheduler:view',
            {'pk': sc_item.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # Request to delete
        resp = self.get_response(
            'scheduler:delete',
            {'pk': sc_item.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # DELETE
        resp = self.get_response(
            'scheduler:delete',
            {'pk': sc_item.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(ScheduledAction.objects.count(), 0)

    def test_views_json(self):
        """Test the use of forms in to schedule actions."""
        # Index of all scheduled actions
        resp = self.get_response('scheduler:index')
        self.assertTrue(status.is_success(resp.status_code))

        # Get the email action object
        action = self.workflow.actions.get(name='json action')

        # Get the form to schedule this action
        resp = self.get_response('scheduler:create', {'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))

        # POST the form to schedule this action
        resp = self.get_response(
            'scheduler:create',
            {'pk': action.id},
            method='POST',
            req_params={
                'name': 'First scheduling round',
                'execute': '05/31/2119 14:35',
                'token': 'faketoken',
            })
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(ScheduledAction.objects.count(), 1)

        # Change the name of the scheduled item
        sc_item = ScheduledAction.objects.first()
        resp = self.get_response(
            'scheduler:edit',
            {'pk': sc_item.id},
            method='POST',
            req_params={
                'name': 'First scheduling round2',
                'execute': '05/31/2119 14:35',
                'token': 'faketoken',
            })
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(ScheduledAction.objects.count(), 1)
        sc_item.refresh_from_db()

        self.assertEqual(sc_item.name, 'First scheduling round2')

        # Select the item_column for confirmation
        sc_item = ScheduledAction.objects.first()
        resp = self.get_response(
            'scheduler:edit',
            {'pk': sc_item.id},
            method='POST',
            req_params={
                'name': 'First scheduling round3',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'execute': '05/31/2119 14:35',
                'token': 'faketoken',
            })
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(ScheduledAction.objects.count(), 1)

        # Index of all scheduled actions (to execute the table render)
        resp = self.get_response('scheduler:index')
        self.assertTrue(status.is_success(resp.status_code))

        # Request to delete
        resp = self.get_response(
            'scheduler:delete',
            {'pk': sc_item.id},
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))

        # DELETE
        resp = self.get_response(
            'scheduler:delete',
            {'pk': sc_item.id},
            method='POST',
            is_ajax=True)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(ScheduledAction.objects.count(), 0)
