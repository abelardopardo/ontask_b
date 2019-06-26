# -*- coding: utf-8 -*-

import os
import test

from django.conf import settings
from django.shortcuts import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

from ontask.apps.action.models import Action
from ontask.apps.scheduler.models import ScheduledAction


class ScheduleApiCreate(test.OnTaskApiTestCase):
    """Test schedule creation through API"""

    fixtures = ['three_actions']
    filename = os.path.join(
        settings.BASE_DIR(),
        'scheduler',
        'fixtures',
        'three_actions.sql'
    )

    s_name = 'Scheduling first JSON'
    s_desc = 'First JSON intervention'
    s_execute = '2119-05-03 12:32:18+10:30'

    def setUp(self):
        super().setUp()
        # Get the token for authentication and set credentials in client
        token = Token.objects.get(user__email='instructor01@bogus.com')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        test.pg_restore_table(self.filename)

    def tearDown(self):
        test.delete_all_tables()
        super().tearDown()

    def test_schedule_email(self):
        action_name = 'simple action'

        s_subject = 'subject'
        # Get list of workflows
        response = self.client.get(reverse('scheduler:api_scheduled_email'))

        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        # Get the action
        action = Action.objects.get(name=action_name, workflow__name='wflow1')

        # Schedule one of the actions
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': self.s_name,
                'description_text': self.s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
                'payload': {
                        'subject': s_subject,
                        'cc_email': [],
                        'bcc_email': [],
                        'track_read': False,
                        'send_confirmation': False,
                },
            },
            format='json')

        # Element has been scheduled
        self.assertEqual(response.status_code, 201)

        sch_item = ScheduledAction.objects.get(action=action)
        self.assertEqual(sch_item.name, self.s_name)
        self.assertEqual(sch_item.description_text, self.s_desc)
        self.assertEqual(sch_item.action, action)
        self.assertEqual(sch_item.payload['subject'], s_subject)

        # Update the element
        response = self.client.put(
            reverse('scheduler:api_rud_email', kwargs={'pk': sch_item.id}),
            {
                'name': self.s_name + '2',
                'description_text': self.s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
                'payload': {
                    'subject': s_subject,
                    'cc_email': [],
                    'bcc_email': [],
                    'track_read': False,
                    'send_confirmation': False,
                },
            },
            format='json'
        )

        # Element has been scheduled
        self.assertTrue(status.is_success(response.status_code))

        sch_item = ScheduledAction.objects.get(action=action)
        self.assertEqual(sch_item.name, self.s_name + '2')

        # Delete the element
        response = self.client.delete(
            reverse('scheduler:api_rud_email', kwargs={'pk': sch_item.id})
        )
        self.assertEqual(response.status_code, 204)



    def test_schedule_json(self):
        action_name = 'json action'
        # Get list of workflows
        response = self.client.get(reverse('scheduler:api_scheduled_json'))

        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        # Get the action
        action = Action.objects.get(name=action_name, workflow__name='wflow1')

        # Schedule one of the actions
        response = self.client.post(
            reverse('scheduler:api_scheduled_json'),
            {
                'name': self.s_name,
                'description_text': self.s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
                'payload': {
                    'token': 'whatever',
                    'field1': 'value1',
                    'field2': 'value2',
                },
            },
            format='json')

        # Element has been created
        self.assertEqual(response.status_code, 201)

        sch_item = ScheduledAction.objects.get(action=action)
        self.assertEqual(sch_item.name, self.s_name)
        self.assertEqual(sch_item.description_text, self.s_desc)
        self.assertEqual(sch_item.action, action)

        # Update the element
        response = self.client.put(
            reverse('scheduler:api_rud_json', kwargs={'pk': sch_item.id}),
            {
                'name': self.s_name + '2',
                'description_text': self.s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
                'payload': {
                    'token': 'whatever',
                    'field1': 'value1',
                    'field2': 'value2',
                },
            },
            format='json'
        )

        # Element has been scheduled
        self.assertTrue(status.is_success(response.status_code))

        sch_item = ScheduledAction.objects.get(action=action)
        self.assertEqual(sch_item.name, self.s_name + '2')

        # Delete the element
        response = self.client.delete(
            reverse('scheduler:api_rud_json', kwargs={'pk': sch_item.id})
        )
        self.assertEqual(response.status_code, 204)

        # Schedule the action with the wrong function
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': self.s_name,
                'description_text': self.s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
                'payload': {
                    'token': 'whatever',
                    'field1': 'value1',
                    'field2': 'value2',
                },
            },
            format='json')

        # Element has been created
        self.assertEqual(response.status_code, 500)

    def test_action_from_other_user(self):

        action_name = 'email action'

        # Get list of workflows
        response = self.client.get(reverse('scheduler:api_scheduled_email'))

        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        # Get the action
        action = Action.objects.get(
            name=action_name,
            workflow__name='user2 workflow')

        # Schedule one of the actions
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': self.s_name,
                'description_text': self.s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
                'payload': {
                        'subject': 'subject',
                        'cc_email': [],
                        'bcc_email': [],
                        'track_read': False,
                        'send_confirmation': False,
                },
            },
            format='json')

        # Element has been scheduled
        self.assertEqual(response.status_code, 500)
        self.assertTrue('Incorrect permission' in response.data['detail'])

    def test_anomalies(self):

        action_name = 'simple action'

        s_name = 'Scheduling first email'
        s_desc = 'First email intervention'
        s_execute = '2119-05-02 12:32:18+10:30'
        s_subject = 'subject'
        # Get list of workflows
        response = self.client.get(reverse('scheduler:api_scheduled_email'))

        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        # Get the action
        action = Action.objects.get(name=action_name)

        # Schedule the action with the wrong function
        response = self.client.post(
            reverse('scheduler:api_scheduled_json'),
            {
                'name': self.s_name,
                'description_text': self.s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
                'payload': {
                    'field1': 'value1',
                    'field2': 'value2',
                },
            },
            format='json')

        # Error detected
        self.assertEqual(response.status_code, 500)

        # Schedule the action in the past
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': s_name,
                'description_text': s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': '2000-11-12 12:05:07+10:30',
                'payload': {
                        'subject': s_subject,
                        'cc_email': [],
                        'bcc_email': [],
                        'track_read': False,
                        'send_confirmation': False,
                },
            },
            format='json')
        self.assertEqual(response.status_code, 500)
        self.assertTrue('Invalid date/time' in response.data['detail'])

        # Schedule with the wrong item column
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': s_name,
                'description_text': s_desc,
                'action': action.id,
                'item_column': 'email2',
                'execute': self.s_execute,
                'payload': {
                        'subject': s_subject,
                        'cc_email': [],
                        'bcc_email': [],
                        'track_read': False,
                        'send_confirmation': False,
                },
            },
            format='json')

        self.assertEqual(response.status_code, 500)
        self.assertTrue('Invalid column' in response.data['detail'])

        # Schedule with the wrong exclude value type
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': s_name,
                'description_text': s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
                'exclude_values': {},
                'payload': {
                        'subject': s_subject,
                        'cc_email': [],
                        'bcc_email': [],
                        'track_read': False,
                        'send_confirmation': False,
                },
            },
            format='json')

        self.assertEqual(response.status_code, 500)
        self.assertTrue('must be a list' in response.data['detail'])

        # Schedule without payload
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': s_name,
                'description_text': s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
            },
            format='json')

        self.assertEqual(response.status_code, 500)
        self.assertTrue('needs a payload' in response.data['detail'])

        # Schedule without subject
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': s_name,
                'description_text': s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
                'payload': {
                    'cc_email': [],
                    'bcc_email': [],
                    'track_read': False,
                    'send_confirmation': False,
                },
            },
            format='json')

        self.assertEqual(response.status_code, 500)
        self.assertTrue('needs a subject' in response.data['detail'])

        # Schedule without item_column
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': s_name,
                'description_text': s_desc,
                'action': action.id,
                'execute': self.s_execute,
                'payload': {
                    'subject': s_subject,
                    'cc_email': [],
                    'bcc_email': [],
                    'track_read': False,
                    'send_confirmation': False,
                },
            },
            format='json')

        self.assertEqual(response.status_code, 500)
        self.assertTrue('needs an item_column' in response.data['detail'])

        # Schedule with item column with incorrect emails
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': s_name,
                'description_text': s_desc,
                'action': action.id,
                'item_column': 'sid',
                'execute': self.s_execute,
                'payload': {
                    'subject': s_subject,
                    'cc_email': [],
                    'bcc_email': [],
                    'track_read': False,
                    'send_confirmation': False,
                },
            },
            format='json')

        self.assertEqual(response.status_code, 500)
        self.assertTrue(
            'addresses has incorrect values' in response.data['detail'])

        # Schedule with incorrect vlues in cc_email
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': s_name,
                'description_text': s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
                'payload': {
                    'subject': s_subject,
                    'cc_email': 1,
                    'bcc_email': [],
                    'track_read': False,
                    'send_confirmation': False,
                },
            },
            format='json')

        self.assertEqual(response.status_code, 500)
        self.assertTrue(
            'must be a comma-separated list of emails'
            in response.data['detail'])

        # Schedule with incorrect vlues in cc_email
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': s_name,
                'description_text': s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
                'payload': {
                    'subject': s_subject,
                    'cc_email': ['xxx', 'yyy'],
                    'bcc_email': [],
                    'track_read': False,
                    'send_confirmation': False,
                },
            },
            format='json')

        self.assertEqual(response.status_code, 500)
        self.assertTrue(
            'must be a comma-separated list of emails'
            in response.data['detail'])

        # Schedule with incorrect vlues in bcc_email
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': s_name,
                'description_text': s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
                'payload': {
                    'subject': s_subject,
                    'cc_email': [],
                    'bcc_email': 1,
                    'track_read': False,
                    'send_confirmation': False,
                },
            },
            format='json')

        self.assertEqual(response.status_code, 500)
        self.assertTrue(
            'must be a comma-separated list of emails'
            in response.data['detail'])

        # Schedule with incorrect vlues in bcc_email
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': s_name,
                'description_text': s_desc,
                'action': action.id,
                'item_column': 'email',
                'execute': self.s_execute,
                'payload': {
                    'subject': s_subject,
                    'cc_email': [],
                    'bcc_email': ['xxx', 'yyy'],
                    'track_read': False,
                    'send_confirmation': False,
                },
            },
            format='json')

        self.assertEqual(response.status_code, 500)
        self.assertTrue(
            'must be a comma-separated list of emails'
            in response.data['detail'])
