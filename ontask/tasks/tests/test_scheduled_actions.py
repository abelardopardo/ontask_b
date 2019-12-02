# -*- coding: utf-8 -*-

"""Test to verify that the scheduled actions are properly executed."""
from datetime import datetime, timedelta
import os

from celery.contrib.testing.worker import start_worker
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import connection
from psycopg2 import sql
import pytz

from ontask import OnTaskSharedState, models, tasks
from ontask.celery import app
import test


class ScheduledOperationTaskTestCase(test.OnTaskTestCase):
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
        action = models.Action.objects.get(name='send email')

        scheduled_item = models.ScheduledOperation(
            user=user,
            operation_type=models.Action.PERSONALIZED_TEXT,
            name='send email action',
            action=action,
            execute=datetime.now(pytz.timezone(settings.TIME_ZONE)).replace(
                second=0),
            status=models.scheduler.STATUS_PENDING,
            item_column=action.workflow.columns.get(name='email'),
            payload={
                'subject': 'Email subject',
                'cc_email': '',
                'bcc_email': '',
                'send_confirmation': False,
                'track_read': False})

        scheduled_item.save()

        # Execute the scheduler
        tasks.execute_scheduled_operations_task(True)

        scheduled_item.refresh_from_db()
        assert scheduled_item.status == models.scheduler.STATUS_DONE
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
        action = models.Action.objects.get(name='send json')

        scheduled_item = models.ScheduledOperation(
            user=user,
            operation_type=models.Action.PERSONALIZED_JSON,
            name='JSON scheduled action',
            action=action,
            execute=datetime.now(pytz.timezone(settings.TIME_ZONE)).replace(
                second=0),
            status=models.scheduler.STATUS_PENDING,
            item_column=action.workflow.columns.get(name='email'),
            payload={'token': token})
        scheduled_item.save()

        # Execute the scheduler
        tasks.execute_scheduled_operations_task(True)

        scheduled_item.refresh_from_db()
        json_outbox = OnTaskSharedState.json_outbox
        assert scheduled_item.status == models.scheduler.STATUS_DONE
        assert len(json_outbox) == 3
        assert all(item['target'] == action.target_url for item in json_outbox)
        assert all(token in item['auth'] for item in json_outbox)


    def test_scheduled_send_list_action(self):
        """Create a scheduled send list action and execute it."""

        user = get_user_model().objects.get(email='instructor01@bogus.com')

        # User must exist
        self.assertIsNotNone(user, 'User instructor01@bogus.com not found')
        action = models.Action.objects.get(name='send list')

        scheduled_item = models.ScheduledOperation(
            user=user,
            operation_type=models.Action.EMAIL_LIST,
            name='send list scheduled action',
            action=action,
            execute=datetime.now(pytz.timezone(settings.TIME_ZONE)).replace(
                second=0),
            status=models.scheduler.STATUS_PENDING,
            payload={
                'email_to': 'recipient@bogus.com',
                'subject': 'Action subject',
                'cc_email': '',
                'bcc_email': ''})
        scheduled_item.save()

        # Execute the scheduler
        tasks.execute_scheduled_operations_task(True)

        scheduled_item.refresh_from_db()
        assert scheduled_item.status == models.scheduler.STATUS_DONE
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
        action = models.Action.objects.get(name='send json list')

        scheduled_item = models.ScheduledOperation(
            user=user,
            operation_type=models.Action.JSON_LIST,
            name='JSON List scheduled action',
            action=action,
            execute=datetime.now(pytz.timezone(settings.TIME_ZONE)).replace(
                second=0),
            status=models.scheduler.STATUS_PENDING,
            payload={'token': token})
        scheduled_item.save()

        # Execute the scheduler
        tasks.execute_scheduled_operations_task(True)

        json_outbox = OnTaskSharedState.json_outbox
        scheduled_item.refresh_from_db()
        assert scheduled_item.status == models.scheduler.STATUS_DONE
        assert len(json_outbox) == 1
        assert all(token in item['auth'] for item in json_outbox)

    def test_scheduled_incremental_email_action(self):
        """Test an incremental scheduled action."""
        # Modify the data table so that initially all records have registered
        # equal to alse
        workflow = models.Workflow.objects.all().first()
        with connection.cursor() as cursor:
            query = sql.SQL('UPDATE {0} SET {1} = false').format(
                sql.Identifier(workflow.get_data_frame_table_name()),
                sql.Identifier('registered'))
            cursor.execute(query)

        user = get_user_model().objects.get(email='instructor01@bogus.com')

        # User must exist
        self.assertIsNotNone(user, 'User instructor01@bogus.com not found')
        action = models.Action.objects.get(name='send email incrementally')

        now = datetime.now(pytz.timezone(settings.TIME_ZONE)).replace(second=0)
        scheduled_item = models.ScheduledOperation(
            user=user,
            operation_type=models.Action.PERSONALIZED_TEXT,
            name='send email action incrementally',
            action=action,
            execute=now,
            execute_until=now + timedelta(hours=1),
            status=models.scheduler.STATUS_PENDING,
            item_column=action.workflow.columns.get(name='email'),
            payload={
                'subject': 'Email subject',
                'cc_email': '',
                'bcc_email': '',
                'send_confirmation': False,
                'track_read': False})
        scheduled_item.save()

        # Execute the scheduler for the first time
        tasks.execute_scheduled_operations_task(True)

        # Event stil pending, with no values in exclude values
        scheduled_item.refresh_from_db()
        assert scheduled_item.status == models.scheduler.STATUS_PENDING
        assert scheduled_item.exclude_values == []

        # Modify one of the values in the matrix
        with connection.cursor() as cursor:
            query = sql.SQL(
                'UPDATE {0} SET {1} = true WHERE {2} = {3}').format(
                    sql.Identifier(workflow.get_data_frame_table_name()),
                    sql.Identifier('registered'),
                    sql.Identifier('email'),
                    sql.Placeholder())
            cursor.execute(query, ['student01@bogus.com'])

        # Execute the scheduler for the first time
        tasks.execute_scheduled_operations_task(True)

        # Event stil pending, with no values in exclude values
        scheduled_item.refresh_from_db()
        assert scheduled_item.status == models.scheduler.STATUS_PENDING
        assert scheduled_item.exclude_values == ['student01@bogus.com']

        # Modify one of the values in the matrix
        with connection.cursor() as cursor:
            query = sql.SQL(
                'UPDATE {0} SET {1} = true WHERE {2} = {3}').format(
                    sql.Identifier(workflow.get_data_frame_table_name()),
                    sql.Identifier('registered'),
                    sql.Identifier('email'),
                    sql.Placeholder())
            cursor.execute(query, ['student02@bogus.com'])

        # Execute the scheduler for the first time
        tasks.execute_scheduled_operations_task(True)

        # Event stil pending, with no values in exclude values
        scheduled_item.refresh_from_db()
        assert scheduled_item.status == models.scheduler.STATUS_PENDING
        assert scheduled_item.exclude_values == [
            'student01@bogus.com',
            'student02@bogus.com']

        # Modify one of the values in the matrix
        with connection.cursor() as cursor:
            query = sql.SQL(
                'UPDATE {0} SET {1} = true WHERE {2} = {3}').format(
                    sql.Identifier(workflow.get_data_frame_table_name()),
                    sql.Identifier('registered'),
                    sql.Identifier('email'),
                    sql.Placeholder())
            cursor.execute(query, ['student03@bogus.com'])

        # Execute the scheduler for the first time
        tasks.execute_scheduled_operations_task(True)

        # Event stil pending, with no values in exclude values
        scheduled_item.refresh_from_db()
        assert scheduled_item.status == models.scheduler.STATUS_PENDING
        assert scheduled_item.exclude_values == [
            'student01@bogus.com',
            'student02@bogus.com',
            'student03@bogus.com']

        # Execute the scheduler for the first time
        tasks.execute_scheduled_operations_task(True)

        # Event stil pending, with no values in exclude values
        scheduled_item.refresh_from_db()
        assert scheduled_item.status == models.scheduler.STATUS_PENDING
        assert scheduled_item.exclude_values == [
            'student01@bogus.com',
            'student02@bogus.com',
            'student03@bogus.com']
