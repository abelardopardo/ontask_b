# -*- coding: utf-8 -*-

"""Test the views for the scheduler pages."""

import os
import test
from typing import Mapping, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.urls import reverse

import scheduler.views
from scheduler.models import ScheduledAction
from workflow.models import Workflow


class SchedulerForms(test.OnTaskTestCase):
    """Test schedule creation through forms."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    fixtures = ['three_actions']
    filename = os.path.join(
        settings.BASE_DIR(),
        'scheduler',
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
        req = self.get_request(reverse('scheduler:index'))
        resp = scheduler.views.index(req)
        self.assertEqual(resp.status_code, 200)

        # Get the email action object
        action = self.workflow.actions.get(name='simple action')

        # Get the form to schedule this action
        req = self.get_request(
            reverse('scheduler:create', kwargs={'pk': action.id}))
        resp = scheduler.views.edit(req, pk=action.id)
        self.assertEqual(resp.status_code, 200)

        # POST the form to schedule this action
        req = self.get_request(
            reverse('scheduler:create', kwargs={'pk': action.id}),
            'POST',
            {
                'name': 'First scheduling round',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'execute': '05/31/2119 14:35',
                'subject': 'Subject text',
            },
        )
        resp = scheduler.views.edit(req, pk=action.id)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ScheduledAction.objects.count(), 1)

        # Change the name of the scheduled item
        sc_item = ScheduledAction.objects.first()
        req = self.get_request(
            reverse('scheduler:edit', kwargs={'pk': sc_item.id}),
            'POST',
            {
                'name': 'First scheduling round2',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'execute': '05/31/2119 14:35',
                'subject': 'Subject text',
            },
        )
        resp = scheduler.views.edit(req, pk=sc_item.id)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ScheduledAction.objects.count(), 1)
        sc_item.refresh_from_db()

        self.assertEqual(sc_item.name, 'First scheduling round2')

        # Select the confirm items
        sc_item = ScheduledAction.objects.first()
        req = self.get_request(
            reverse('scheduler:edit', kwargs={'pk': sc_item.id}),
            'POST',
            {
                'name': 'First scheduling round3',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'confirm_items': True,
                'execute': '05/31/2119 14:35',
                'subject': 'Subject text',
            },
        )
        resp = scheduler.views.edit(req, pk=sc_item.id)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(ScheduledAction.objects.count(), 1)

        # Index of all scheduled actions (to execute the table render)
        req = self.get_request(reverse('scheduler:index'))
        resp = scheduler.views.index(req)
        self.assertEqual(resp.status_code, 200)

        # View the information with a JSON request
        req = self.get_ajax_request(
            reverse('scheduler:view', kwargs={'pk': sc_item.id}))
        resp = scheduler.views.view(req, pk=sc_item.id)
        self.assertEqual(resp.status_code, 200)

        # Request to delete
        req = self.get_ajax_request(
            reverse('scheduler:delete', kwargs={'pk': sc_item.id}))
        resp = scheduler.views.delete(req, pk=sc_item.id)
        self.assertEqual(resp.status_code, 200)

        # DELETE
        req = self.get_ajax_request(
            reverse('scheduler:delete', kwargs={'pk': sc_item.id}),
            'POST'
        )
        resp = scheduler.views.delete(req, pk=sc_item.id)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ScheduledAction.objects.count(), 0)

    def test_views_json(self):
        """Test the use of forms in to schedule actions."""
        # Index of all scheduled actions
        req = self.get_request(reverse('scheduler:index'))
        resp = scheduler.views.index(req)
        self.assertEqual(resp.status_code, 200)

        # Get the email action object
        action = self.workflow.actions.get(name='json action')

        # Get the form to schedule this action
        req = self.get_request(
            reverse('scheduler:create', kwargs={'pk': action.id}))
        resp = scheduler.views.edit(req, pk=action.id)
        self.assertEqual(resp.status_code, 200)

        # POST the form to schedule this action
        req = self.get_request(
            reverse('scheduler:create', kwargs={'pk': action.id}),
            'POST',
            {
                'name': 'First scheduling round',
                'execute': '05/31/2119 14:35',
                'token': 'faketoken',
            },
        )
        resp = scheduler.views.edit(req, pk=action.id)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ScheduledAction.objects.count(), 1)

        # Change the name of the scheduled item
        sc_item = ScheduledAction.objects.first()
        req = self.get_request(
            reverse('scheduler:edit', kwargs={'pk': sc_item.id}),
            'POST',
            {
                'name': 'First scheduling round2',
                'execute': '05/31/2119 14:35',
                'token': 'faketoken',
            },
        )
        resp = scheduler.views.edit(req, pk=sc_item.id)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ScheduledAction.objects.count(), 1)
        sc_item.refresh_from_db()

        self.assertEqual(sc_item.name, 'First scheduling round2')

        # Select the item_column for confirmation
        sc_item = ScheduledAction.objects.first()
        req = self.get_request(
            reverse('scheduler:edit', kwargs={'pk': sc_item.id}),
            'POST',
            {
                'name': 'First scheduling round3',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'execute': '05/31/2119 14:35',
                'token': 'faketoken',
            },
        )
        resp = scheduler.views.edit(req, pk=sc_item.id)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(ScheduledAction.objects.count(), 1)

        # Index of all scheduled actions (to execute the table render)
        req = self.get_request(reverse('scheduler:index'))
        resp = scheduler.views.index(req)
        self.assertEqual(resp.status_code, 200)

        # Request to delete
        req = self.get_ajax_request(
            reverse('scheduler:delete', kwargs={'pk': sc_item.id}))
        resp = scheduler.views.delete(req, pk=sc_item.id)
        self.assertEqual(resp.status_code, 200)

        # DELETE
        req = self.get_ajax_request(
            reverse('scheduler:delete', kwargs={'pk': sc_item.id}),
            'POST'
        )
        resp = scheduler.views.delete(req, pk=sc_item.id)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ScheduledAction.objects.count(), 0)
