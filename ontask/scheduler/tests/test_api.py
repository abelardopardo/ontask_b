"""Test scheduler API."""

from django.shortcuts import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

from ontask import models, tests


class ScheduleApiBasic(tests.ThreeActionsFixture, tests.OnTaskApiTestCase):
    """Test schedule creation through API"""

    s_name = 'Scheduling first JSON'
    s_desc = 'First JSON intervention'
    s_execute = '2119-05-03 12:32:18+10:30'
    api_error_msg = 'Scheduled action could not be created'
    log_msg = 'ERROR:ontask:' + api_error_msg + ': '

    def setUp(self):
        super().setUp()
        # Get the token for authentication and set credentials in client
        token = Token.objects.get(user__email='instructor01@bogus.com')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


class ScheduleApiCreate(ScheduleApiBasic):
    """Test schedule creation through API"""

    def test(self):
        action_name = 'email action'

        # Get list of workflows
        response = self.client.get(reverse('scheduler:api_scheduled_email'))

        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        # Get the action
        action = models.Action.objects.get(
            name=action_name,
            workflow__name='user2 workflow')

        with self.assertLogs(logger='ontask', level='ERROR') as log_context:
            # Schedule one of the actions
            response = self.client.post(
                reverse('scheduler:api_scheduled_email'),
                {
                    'name': self.s_name,
                    'description_text': self.s_desc,
                    'operation_type': 'action_run_personalized_email',
                    'workflow': action.workflow_id,
                    'action': action.id,
                    'execute_start': self.s_execute,
                    'payload': {
                        'item_column': 'email',
                        'subject': 'subject',
                        'cc_email': '',
                        'bcc_email': '',
                        'track_read': False,
                        'send_confirmation': False,
                    },
                },
                format='json')
    
            # Element has been scheduled
            self.assertEqual(response.status_code, 500)
            self.assertIn(self.api_error_msg, response.data['detail'])
            self.assertIn(
                self.log_msg +
                'Incorrect permission to manipulate workflow.',
                log_context.output)


class ScheduleApiAnomalies(ScheduleApiBasic):
    """Test schedule creation through API"""

    def test(self):
        action_name = 'simple action'

        s_name = 'Scheduling first email'
        s_desc = 'First email intervention'
        s_subject = 'subject'
        # Get list of workflows
        response = self.client.get(reverse('scheduler:api_scheduled_email'))

        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        # Get the action
        action = models.Action.objects.get(name=action_name)

        # Schedule the action with the wrong function
        response = self.client.post(
            reverse('scheduler:api_scheduled_json'),
            {
                'name': self.s_name,
                'description_text': self.s_desc,
                'operation_type': 'action_run_personalized_email',
                'workflow': action.workflow_id,
                'action': action.id,
                'execute_start': self.s_execute,
                'payload': {
                    'item_column': 'email',
                    'field1': 'value1',
                    'field2': 'value2',
                },
            },
            format='json')

        # Error detected
        self.assertEqual(response.status_code, 500)

        with self.assertLogs(logger='ontask', level='ERROR') as log_context:
            # Schedule the action in the past
            response = self.client.post(
                reverse('scheduler:api_scheduled_email'),
                {
                    'name': s_name,
                    'description_text': s_desc,
                    'operation_type': 'action_run_personalized_email',
                    'workflow': action.workflow_id,
                    'action': action.id,
                    'execute_start': '2000-11-12 12:05:07+10:30',
                    'payload': {
                        'item_column': 'email',
                        'subject': s_subject,
                        'cc_email': '',
                        'bcc_email': '',
                        'track_read': False,
                        'send_confirmation': False,
                    },
                },
                format='json')
            self.assertEqual(response.status_code, 500)
            self.assertIn(self.api_error_msg, response.data['detail'])
            self.assertIn(
                self.log_msg +
                'Execution time is in the past. No execution possible.',
                log_context.output)

        with self.assertLogs(logger='ontask', level='ERROR') as log_context:
            # Schedule with the wrong item column
            response = self.client.post(
                reverse('scheduler:api_scheduled_email'),
                {
                    'name': s_name,
                    'description_text': s_desc,
                    'operation_type': 'action_run_personalized_email',
                    'workflow': action.workflow_id,
                    'action': action.id,
                    'execute_start': self.s_execute,
                    'payload': {
                        'item_column': 'email2',
                        'subject': s_subject,
                        'cc_email': '',
                        'bcc_email': '',
                        'track_read': False,
                        'send_confirmation': False,
                    },
                },
                format='json')

            self.assertEqual(response.status_code, 500)
            self.assertTrue(self.api_error_msg in response.data['detail'])
            self.assertIn(
                self.log_msg + 'Invalid column name for selecting items.',
                log_context.output)

        with self.assertLogs(logger='ontask', level='ERROR') as log_context:
            # Schedule with the wrong exclude value type
            response = self.client.post(
                reverse('scheduler:api_scheduled_email'),
                {
                    'name': s_name,
                    'description_text': s_desc,
                    'action': action.id,
                    'operation_type': 'action_run_personalized_email',
                    'workflow': action.workflow_id,
                    'execute_start': self.s_execute,
                    'payload': {
                        'item_column': 'email',
                        'exclude_values': {},
                        'subject': s_subject,
                        'cc_email': '',
                        'bcc_email': '',
                        'track_read': False,
                        'send_confirmation': False,
                    },
                },
                format='json')

            self.assertEqual(response.status_code, 500)
            self.assertTrue(self.api_error_msg in response.data['detail'])
            self.assertIn(
                self.log_msg +
                'Exclude values must be a list.',
                log_context.output)

        with self.assertLogs(logger='ontask', level='ERROR') as log_context:
            # Schedule without payload
            response = self.client.post(
                reverse('scheduler:api_scheduled_email'),
                {
                    'name': s_name,
                    'description_text': s_desc,
                    'operation_type': 'action_run_personalized_email',
                    'workflow': action.workflow_id,
                    'action': action.id,
                    'execute_start': self.s_execute,
                },
                format='json')

            self.assertEqual(response.status_code, 500)
            self.assertTrue(self.api_error_msg in response.data['detail'])
            self.assertIn(
                self.log_msg + 'Scheduled objects need a payload.',
                log_context.output)

        with self.assertLogs(logger='ontask', level='ERROR') as log_context:
            # Schedule without subject
            response = self.client.post(
                reverse('scheduler:api_scheduled_email'),
                {
                    'name': s_name,
                    'description_text': s_desc,
                    'operation_type': 'action_run_personalized_email',
                    'workflow': action.workflow_id,
                    'action': action.id,
                    'execute_start': self.s_execute,
                    'payload': {
                        'item_column': 'email',
                        'cc_email': '',
                        'bcc_email': '',
                        'track_read': False,
                        'send_confirmation': False,
                    },
                },
                format='json')

            self.assertEqual(response.status_code, 500)
            self.assertTrue(self.api_error_msg in response.data['detail'])
            self.assertIn(
                self.log_msg + 'Personalized text needs a subject.',
                log_context.output)

        with self.assertLogs(logger='ontask', level='ERROR') as log_context:
            # Schedule without item_column
            response = self.client.post(
                reverse('scheduler:api_scheduled_email'),
                {
                    'name': s_name,
                    'description_text': s_desc,
                    'operation_type': 'action_run_personalized_email',
                    'workflow': action.workflow_id,
                    'action': action.id,
                    'execute_start': self.s_execute,
                    'payload': {
                        'subject': s_subject,
                        'cc_email': '',
                        'bcc_email': '',
                        'track_read': False,
                        'send_confirmation': False,
                    },
                },
                format='json')

            self.assertEqual(response.status_code, 500)
            self.assertTrue(self.api_error_msg in response.data['detail'])
            self.assertIn(
                self.log_msg +
                'Personalized text need a column name in payload '
                'field item_column.',
                log_context.output)

        with self.assertLogs(logger='ontask', level='ERROR') as log_context:
            # Schedule with item column with incorrect emails
            response = self.client.post(
                reverse('scheduler:api_scheduled_email'),
                {
                    'name': s_name,
                    'description_text': s_desc,
                    'operation_type': 'action_run_personalized_email',
                    'workflow': action.workflow_id,
                    'action': action.id,
                    'execute_start': self.s_execute,
                    'payload': {
                        'item_column': 'sid',
                        'subject': s_subject,
                        'cc_email': '',
                        'bcc_email': '',
                        'track_read': False,
                        'send_confirmation': False,
                    },
                },
                format='json')

            self.assertEqual(response.status_code, 500)
            self.assertTrue(self.api_error_msg in response.data['detail'])
            self.assertIn(
                self.log_msg + 'Incorrect email value "1".',
                log_context.output)

        with self.assertLogs(logger='ontask', level='ERROR') as log_context:
            # Schedule with incorrect values in cc_email
            response = self.client.post(
                reverse('scheduler:api_scheduled_email'),
                {
                    'name': s_name,
                    'description_text': s_desc,
                    'operation_type': 'action_run_personalized_email',
                    'workflow': action.workflow_id,
                    'action': action.id,
                    'execute_start': self.s_execute,
                    'payload': {
                        'item_column': 'email',
                        'subject': s_subject,
                        'cc_email': 1,
                        'bcc_email': '',
                        'track_read': False,
                        'send_confirmation': False,
                    },
                },
                format='json')

            self.assertEqual(response.status_code, 500)
            self.assertTrue(self.api_error_msg in response.data['detail'])
            self.assertIn(
                self.log_msg +
                'cc_email must be a space-separated list of emails.',
                log_context.output)

        with self.assertLogs(logger='ontask', level='ERROR') as log_context:
            # Schedule with incorrect values in cc_email
            response = self.client.post(
                reverse('scheduler:api_scheduled_email'),
                {
                    'name': s_name,
                    'description_text': s_desc,
                    'operation_type': 'action_run_personalized_email',
                    'workflow': action.workflow_id,
                    'action': action.id,
                    'execute_start': self.s_execute,
                    'payload': {
                        'item_column': 'email',
                        'subject': s_subject,
                        'cc_email': 'xxx yyy',
                        'bcc_email': '',
                        'track_read': False,
                        'send_confirmation': False,
                    },
                },
                format='json')

            self.assertEqual(response.status_code, 500)
            self.assertTrue(self.api_error_msg in response.data['detail'])
            self.assertIn(
                self.log_msg +
                'cc_email must be a space-separated list of emails.',
                log_context.output)

        with self.assertLogs(logger='ontask', level='ERROR') as log_context:
            # Schedule with incorrect values in bcc_email
            response = self.client.post(
                reverse('scheduler:api_scheduled_email'),
                {
                    'name': s_name,
                    'description_text': s_desc,
                    'operation_type': 'action_run_personalized_email',
                    'workflow': action.workflow_id,
                    'action': action.id,
                    'execute_start': self.s_execute,
                    'payload': {
                        'item_column': 'email',
                        'subject': s_subject,
                        'cc_email': '',
                        'bcc_email': 1,
                        'track_read': False,
                        'send_confirmation': False,
                    },
                },
                format='json')

            self.assertEqual(response.status_code, 500)
            self.assertTrue(self.api_error_msg in response.data['detail'])
            self.assertIn(
                self.log_msg +
                'bcc_email must be a space-separated list of emails.',
                log_context.output)

        with self.assertLogs(logger='ontask', level='ERROR') as log_context:
            # Schedule with incorrect values in bcc_email
            response = self.client.post(
                reverse('scheduler:api_scheduled_email'),
                {
                    'name': s_name,
                    'description_text': s_desc,
                    'operation_type': 'action_run_personalized_email',
                    'workflow': action.workflow_id,
                    'action': action.id,
                    'execute_start': self.s_execute,
                    'payload': {
                        'item_column': 'email',
                        'subject': s_subject,
                        'cc_email': '',
                        'bcc_email': 'xxx yyy',
                        'track_read': False,
                        'send_confirmation': False,
                    },
                },
                format='json')

            self.assertEqual(response.status_code, 500)
            self.assertTrue(self.api_error_msg in response.data['detail'])
            self.assertIn(
                self.log_msg +
                'bcc_email must be a space-separated list of emails.',
                log_context.output)


class ScheduleApiEmail(ScheduleApiBasic):
    """Test schedule creation through API"""

    def test(self):
        action_name = 'simple action'

        s_subject = 'subject'
        # Get list of workflows
        response = self.client.get(reverse('scheduler:api_scheduled_email'))

        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        # Get the action
        action = models.Action.objects.get(
            name=action_name,
            workflow__name='wflow1')

        # Schedule one of the actions
        response = self.client.post(
            reverse('scheduler:api_scheduled_email'),
            {
                'name': self.s_name,
                'description_text': self.s_desc,
                'operation_type': 'action_run_personalized_email',
                'workflow': action.workflow_id,
                'action': action.id,
                'execute_start': self.s_execute,
                'payload': {
                    'item_column': 'email',
                    'subject': s_subject,
                    'cc_email': '',
                    'bcc_email': '',
                    'track_read': False,
                    'send_confirmation': False,
                },
            },
            format='json')

        # Element has been scheduled
        self.assertEqual(response.status_code, 201)

        sch_item = models.ScheduledOperation.objects.get(action=action)
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
                'operation_type': 'action_run_personalized_email',
                'workflow': action.workflow_id,
                'action': action.id,
                'execute_start': self.s_execute,
                'payload': {
                    'item_column': 'email',
                    'subject': s_subject,
                    'cc_email': '',
                    'bcc_email': '',
                    'track_read': False,
                    'send_confirmation': False}},
            format='json'
        )

        # Element has been scheduled
        self.assertTrue(status.is_success(response.status_code))

        sch_item = models.ScheduledOperation.objects.get(action=action)
        self.assertEqual(sch_item.name, self.s_name + '2')

        # Delete the element
        response = self.client.delete(
            reverse('scheduler:api_rud_email', kwargs={'pk': sch_item.id})
        )
        self.assertEqual(response.status_code, 204)


class ScheduleApiJSON(ScheduleApiBasic):
    """Test schedule creation through API"""

    def test(self):
        action_name = 'json action'
        # Get list of workflows
        response = self.client.get(reverse('scheduler:api_scheduled_json'))

        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        # Get the action
        action = models.Action.objects.get(
            name=action_name,
            workflow__name='wflow1')

        # Schedule one of the actions
        response = self.client.post(
            reverse('scheduler:api_scheduled_json'),
            {
                'name': self.s_name,
                'description_text': self.s_desc,
                'operation_type': 'action_run_personalized_json',
                'workflow': action.workflow_id,
                'action': action.id,
                'execute_start': self.s_execute,
                'payload': {
                    'item_column': 'email',
                    'token': 'whatever',
                    'field1': 'value1',
                    'field2': 'value2',
                },
            },
            format='json')

        # Element has been created
        self.assertEqual(response.status_code, 201)

        sch_item = models.ScheduledOperation.objects.get(action=action)
        self.assertEqual(sch_item.name, self.s_name)
        self.assertEqual(sch_item.description_text, self.s_desc)
        self.assertEqual(sch_item.action, action)

        # Update the element
        response = self.client.put(
            reverse('scheduler:api_rud_json', kwargs={'pk': sch_item.id}),
            {
                'name': self.s_name + '2',
                'description_text': self.s_desc,
                'operation_type': 'action_run_personalized_json',
                'workflow': action.workflow_id,
                'action': action.id,
                'execute_start': self.s_execute,
                'payload': {
                    'item_column': 'email',
                    'token': 'whatever',
                    'field1': 'value1',
                    'field2': 'value2',
                },
            },
            format='json'
        )

        # Element has been scheduled
        self.assertTrue(status.is_success(response.status_code))

        sch_item = models.ScheduledOperation.objects.get(action=action)
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
                'operation_type': 'action_run_personalized_json',
                'workflow': action.workflow_id,
                'action': action.id,
                'execute_start': self.s_execute,
                'payload': {
                    'item_column': 'email',
                    'token': 'whatever',
                    'field1': 'value1',
                    'field2': 'value2',
                },
            },
            format='json')

        # Element has NOT been created
        self.assertEqual(response.status_code, 500)
