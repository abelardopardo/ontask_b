# -*- coding: utf-8 -*-

"""Test to verify that the scheduled actions are properly executed."""

import os
import test
from datetime import datetime

import pytz
from celery.contrib.testing.worker import start_worker
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail

from ontask import tasks, OnTaskSharedState
from ontask.core.celery import app
from ontask.models import Action, ScheduledAction

class ScheduledActionTaskTestCase(test.OnTaskTestCase):
    """Test the functions to execute through celery."""

    fixtures = ['schedule_actions']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'schedule_actions.sql'
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        app.loader.import_module('celery.contrib.testing.tasks')
        cls.celery_worker = start_worker(app)
        cls.celery_worker.__enter__()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.celery_worker.__exit__(None, None, None)

    def test_scheduled_email_action(self):
        """Create a scheduled send email action and execute it."""

        user = get_user_model().objects.get(email='instructor01@bogus.com')

        # User must exist
        self.assertIsNotNone(user, 'User instructor01@bogus.com not found')
        action = Action.objects.get(name='send email')

        scheduled_item = ScheduledAction(
            user=user,
            name='send email action',
            action=action,
            execute=datetime.now(pytz.timezone(settings.TIME_ZONE)),
            status=ScheduledAction.STATUS_PENDING,
            item_column=action.workflow.columns.get(name='email'),
            payload={
                'subject': 'Email subject',
                'cc_email': '',
                'bcc_email': '',
                'send_confirmation': False,
                'track_read': False})

        scheduled_item.save()

        # Execute the scheduler
        tasks.execute_scheduled_actions_task(True)

        scheduled_item.refresh_from_db()
        assert scheduled_item.status == ScheduledAction.STATUS_DONE
        assert len(mail.outbox) == 2
        assert 'Hi Student Two' in mail.outbox[0].body
        assert 'Hi Student Three' in mail.outbox[1].body

    def test_scheduled_json_action(self):
        """Create a scheduled send list action and execute it."""
        token = 'fake token'

        OnTaskSharedState.json_outbox = []
        settings.EXECUTE_ACTION_JSON_TRANSFER = False

        user = get_user_model().objects.get(email='instructor01@bogus.com')

        # User must exist
        self.assertIsNotNone(user, 'User instructor01@bogus.com not found')
        action = Action.objects.get(name='send json')

        scheduled_item = ScheduledAction(
            user=user,
            name='JSON scheduled action',
            action=action,
            execute=datetime.now(pytz.timezone(settings.TIME_ZONE)),
            status=ScheduledAction.STATUS_PENDING,
            item_column=action.workflow.columns.get(name='email'),
            payload={'token': token})
        scheduled_item.save()

        # Execute the scheduler
        tasks.execute_scheduled_actions_task(True)

        scheduled_item.refresh_from_db()
        json_outbox = OnTaskSharedState.json_outbox
        assert scheduled_item.status == ScheduledAction.STATUS_DONE
        assert len(json_outbox) == 3
        assert all(item['target'] == action.target_url for item in json_outbox)
        assert all(token in item['auth'] for item in json_outbox)


    def test_scheduled_send_list_action(self):
        """Create a scheduled send list action and execute it."""

        user = get_user_model().objects.get(email='instructor01@bogus.com')

        # User must exist
        self.assertIsNotNone(user, 'User instructor01@bogus.com not found')
        action = Action.objects.get(name='send list')

        scheduled_item = ScheduledAction(
            user=user,
            name='send list scheduled action',
            action=action,
            execute=datetime.now(pytz.timezone(settings.TIME_ZONE)),
            status=ScheduledAction.STATUS_PENDING,
            payload={
                'email_to': 'recipient@bogus.com',
                'subject': 'Action subject',
                'cc_email': '',
                'bcc_email': ''})
        scheduled_item.save()

        # Execute the scheduler
        tasks.execute_scheduled_actions_task(True)

        scheduled_item.refresh_from_db()
        assert scheduled_item.status == ScheduledAction.STATUS_DONE
        assert len(mail.outbox) == 1
        assert (
            'student01@bogus.com, student03@bogus.com' in mail.outbox[0].body)

    def test_scheduled_json_list_action(self):
        """Create a scheduled send list action and execute it."""

        token = 'false token'
        settings.EXECUTE_ACTION_JSON_TRANSFER = False
        OnTaskSharedState.json_outbox = []

        user = get_user_model().objects.get(email='instructor01@bogus.com')

        # User must exist
        self.assertIsNotNone(user, 'User instructor01@bogus.com not found')
        action = Action.objects.get(name='send json list')

        scheduled_item = ScheduledAction(
            user=user,
            name='JSON List scheduled action',
            action=action,
            execute=datetime.now(pytz.timezone(settings.TIME_ZONE)),
            status=ScheduledAction.STATUS_PENDING,
            payload={'token': token})
        scheduled_item.save()

        # Execute the scheduler
        tasks.execute_scheduled_actions_task(True)

        json_outbox = OnTaskSharedState.json_outbox
        scheduled_item.refresh_from_db()
        assert scheduled_item.status == ScheduledAction.STATUS_DONE
        assert len(json_outbox) == 1
        assert all(token in item['auth'] for item in json_outbox)

