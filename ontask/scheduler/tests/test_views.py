"""Test the views for the scheduler pages."""
from datetime import datetime, timedelta

from django.conf import settings
import pytz
from rest_framework import status

from ontask import models, tests


class SchedulerFormsBasic(tests.ThreeActionsFixture, tests.OnTaskTestCase):
    """Test schedule creation through forms."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'  # noqa: S105

    s_name = 'Scheduling first JSON'
    s_desc = 'First JSON intervention'
    s_execute = '2119-05-03 12:32:18+10:30'


class SchedulerForms(SchedulerFormsBasic):
    """Test schedule creation through forms."""

    def test(self):
        """Test the use of forms in to schedule actions."""
        # Index of all scheduled actions
        resp = self.get_response('scheduler:index')
        self.assertTrue(status.is_success(resp.status_code))

        # Get the email action object
        action = self.workflow.actions.get(name='simple action')

        # Get the form to schedule this action
        resp = self.get_response(
            'scheduler:create_action_run',
            {'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))

        # POST the form to schedule this action
        resp = self.get_response(
            'scheduler:create_action_run',
            {'pk': action.id},
            method='POST',
            req_params={
                'name': 'First scheduling round',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'execute': '05/31/2119 14:35',
                'subject': 'Subject text',
            })
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(models.ScheduledOperation.objects.count(), 1)

        # Change the name of the scheduled item
        sc_item = models.ScheduledOperation.objects.first()
        resp = self.get_response(
            'scheduler:edit_scheduled_operation',
            {'pk': sc_item.id},
            method='POST',
            req_params={
                'name': 'First scheduling round2',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'execute': '05/31/2119 14:35',
                'subject': 'Subject text',
            })
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(models.ScheduledOperation.objects.count(), 1)
        sc_item.refresh_from_db()

        self.assertEqual(sc_item.name, 'First scheduling round2')

        # Select the confirm items
        sc_item = models.ScheduledOperation.objects.first()
        resp = self.get_response(
            'scheduler:edit_scheduled_operation',
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
        self.assertEqual(models.ScheduledOperation.objects.count(), 1)

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
        self.assertEqual(models.ScheduledOperation.objects.count(), 0)


class SchedulerJSONForms(SchedulerFormsBasic):
    """Test schedule creation through forms."""

    def test_schedule_json_action(self):
        """Test creation of a scheduled execution of json action."""
        # Index of all scheduled actions
        resp = self.get_response('scheduler:index')
        self.assertTrue(status.is_success(resp.status_code))

        # Get the email action object
        action = self.workflow.actions.get(name='json action')

        # Get the form to schedule this action
        resp = self.get_response(
            'scheduler:create_action_run',
            {'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))

        # POST the form to schedule this action
        resp = self.get_response(
            'scheduler:create_action_run',
            {'pk': action.id},
            method='POST',
            req_params={
                'name': 'First scheduling round',
                'execute': '05/31/2119 14:35',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'token': 'faketoken',
            })
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(models.ScheduledOperation.objects.count(), 1)

        # Change the name of the scheduled item
        sc_item = models.ScheduledOperation.objects.first()
        resp = self.get_response(
            'scheduler:edit_scheduled_operation',
            {'pk': sc_item.id},
            method='POST',
            req_params={
                'name': 'First scheduling round2',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'execute': '05/31/2119 14:35',
                'token': 'faketoken',
            })
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(models.ScheduledOperation.objects.count(), 1)
        sc_item.refresh_from_db()

        self.assertEqual(sc_item.name, 'First scheduling round2')

        # Select the item_column for confirmation
        sc_item = models.ScheduledOperation.objects.first()
        resp = self.get_response(
            'scheduler:edit_scheduled_operation',
            {'pk': sc_item.id},
            method='POST',
            req_params={
                'name': 'First scheduling round3',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'confirm_items': True,
                'execute': '05/31/2119 14:35',
                'token': 'faketoken',
            })
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(models.ScheduledOperation.objects.count(), 1)

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
        self.assertEqual(models.ScheduledOperation.objects.count(), 0)


class SchedulerTimesInForms(SchedulerFormsBasic):
    """Test schedule creation through forms."""

    def test(self):
        # Index of all scheduled actions
        resp = self.get_response('scheduler:index')
        self.assertTrue(status.is_success(resp.status_code))

        # Get the email action object
        action = self.workflow.actions.get(name='simple action')

        # Get the form to schedule this action
        resp = self.get_response(
            'scheduler:create_action_run',
            {'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))

        # POST the form to schedule this action with wrong dates
        resp = self.get_response(
            'scheduler:create_action_run',
            {'pk': action.id},
            method='POST',
            req_params={
                'name': 'Second scheduling round',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'multiple_executions': True,
                'frequency': '* * * * *',
                'execute': '05/31/2119 14:35',
                'execute_until': '05/31/2119 14:30',
                'subject': 'Subject text',
            })
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(models.ScheduledOperation.objects.count(), 0)

        # POST the form to schedule this action
        now = datetime.now(pytz.timezone(settings.TIME_ZONE))
        execute = now - timedelta(minutes=5)
        execute_until = now - timedelta(minutes=1)
        resp = self.get_response(
            'scheduler:create_action_run',
            {'pk': action.id},
            method='POST',
            req_params={
                'name': 'Second scheduling round',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'multiple_executions': True,
                'frequency': '* * * * *',
                'execute': execute.strftime('%m/%d/%Y %H:%M:%S'),
                'execute_until': execute_until.strftime('%m/%d/%Y %H:%M:%S'),
                'subject': 'Subject text',
            })
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(models.ScheduledOperation.objects.count(), 0)

        # POST the form to schedule this action
        now = datetime.now(pytz.timezone(settings.TIME_ZONE))
        execute = now - timedelta(minutes=5)
        execute_until = now + timedelta(days=1)
        resp = self.get_response(
            'scheduler:create_action_run',
            {'pk': action.id},
            method='POST',
            req_params={
                'name': 'Second scheduling round',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'multiple_executions': True,
                'frequency': '* * * * *',
                'execute': execute.strftime('%m/%d/%Y %H:%m'),
                'execute_until': execute_until.strftime('%m/%d/%Y %H:%m'),
                'subject': 'Subject text',
            })
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(models.ScheduledOperation.objects.count(), 1)

        # POST the form to schedule this action
        now = datetime.now(pytz.timezone(settings.TIME_ZONE))
        execute = now + timedelta(minutes=5)
        execute_until = now + timedelta(days=15)
        resp = self.get_response(
            'scheduler:create_action_run',
            {'pk': action.id},
            method='POST',
            req_params={
                'name': 'Third scheduling round',
                'item_column': str(self.workflow.columns.get(name='email').id),
                'multiple_executions': True,
                'frequency': '* * * * *',
                'execute': execute.strftime('%m/%d/%Y %H:%m'),
                'execute_until': execute_until.strftime('%m/%d/%Y %H:%m'),
                'subject': 'Subject text',
            })
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(models.ScheduledOperation.objects.count(), 2)
