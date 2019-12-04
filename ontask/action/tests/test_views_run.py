# -*- coding: utf-8 -*-

"""Test views to run actions."""
from datetime import timedelta
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from ontask import OnTaskSharedState, models, tests
from ontask.core import SessionPayload


class ActionViewRunEmailAction(tests.OnTaskTestCase):
    """Test the view to run actio item filter, json and email."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'tests',
        'initial_workflow',
        'initial_workflow.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'BIOL1011'

    def _verify_content(self):
        """Verify the content of the messages received."""
        self.assertTrue(all(
            message.from_email == 'instructor01@bogus.com'
            and message.subject == 'message subject'
            and 'Here are the comments about ' in message.body
            and 'user01@bogus.com' in message.cc
            and 'user02@bogus.com' in message.cc
            and 'user03@bogus.com' in message.bcc
            and 'user04@bogus.com' in message.bcc
            for message in mail.outbox))

    def test_run_action_email_no_filter(self):
        """Run sequence of request to send email without filtering users."""
        self.client.login(email=self.user_email, password=self.user_pwd)
        action = self.workflow.actions.get(name='Midterm comments')
        column = action.workflow.columns.get(name='email')

        # Step 1 invoke the form
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(action.id == payload['action_id'])
        self.assertTrue(
            payload['prev_url'] == reverse(
                'action:run',
                kwargs={'pk': action.id}))
        self.assertTrue(payload['post_url'] == reverse('action:run_done'))
        self.assertTrue('post_url' in payload.keys())
        self.assertTrue(status.is_success(resp.status_code))

        # Step 2 send POST
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'cc_email': 'user01@bogus.com user02@bogus.com',
                'bcc_email': 'user03@bogus.com user04@bogus.com',
                'item_column': column.pk,
                'subject': 'message subject'})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(payload == {})
        self.assertTrue(len(mail.outbox) == action.get_rows_selected())
        self._verify_content()
        self.assertTrue(status.is_success(resp.status_code))

    def test_email_with_filter(self):
        """Run sequence of request to send email without filtering users."""
        self.client.login(email=self.user_email, password=self.user_pwd)

        action = self.workflow.actions.get(name='Midterm comments')
        column = action.workflow.columns.get(name='email')
        exclude_values = ['pzaz8370@bogus.com', 'tdrv2640@bogus.com']

        # Step 1 invoke the form
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(action.id == payload['action_id'])
        self.assertTrue(
            payload['prev_url'] == reverse(
                'action:run',
                kwargs={'pk': action.id}))
        self.assertTrue(payload['post_url'] == reverse('action:run_done'))
        self.assertTrue('post_url' in payload.keys())
        self.assertTrue(status.is_success(resp.status_code))

        # Step 2 send POST
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'item_column': column.pk,
                'cc_email': 'user01@bogus.com user02@bogus.com',
                'bcc_email': 'user03@bogus.com user04@bogus.com',
                'confirm_items': True,
                'subject': 'message subject'})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(payload['confirm_items'])
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)

        # Load the Filter page with a GET
        resp = self.get_response(
            'action:item_filter',
            session_payload=payload)
        self.assertTrue(status.is_success(resp.status_code))

        # Emulate the filter page with a POST
        resp = self.get_response(
            'action:item_filter',
            method='POST',
            req_params={'exclude_values': exclude_values})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(payload['exclude_values'] == exclude_values)
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.url, payload['post_url'])

        # Emulate the redirection to run_done
        resp = self.get_response('action:run_done')
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(payload == {})
        self._verify_content()
        self.assertTrue(
            len(mail.outbox) == (
                action.get_rows_selected() - len(exclude_values)))
        self.assertTrue(status.is_success(resp.status_code))

    def test_run_action_item_filter(self):
        """Test the view to filter items."""
        action = self.workflow.actions.get(name='Midterm comments')
        column = action.workflow.columns.get(name='email')
        payload = {
            'item_column': column.pk,
            'action_id': action.id,
            'button_label': 'Send',
            'valuerange': 2,
            'step': 2,
            'prev_url': reverse('action:run', kwargs={'pk': action.id}),
            'post_url': reverse('action:run_done')}
        resp = self.get_response(
            'action:item_filter',
            session_payload=payload)
        self.assertTrue(status.is_success(resp.status_code))

        # POST
        resp = self.get_response(
            'action:item_filter',
            method='POST',
            req_params={
                'exclude_values': ['ctfh9946@bogus.com'],
            },
            session_payload=payload)
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.url, reverse('action:run_done'))


class ActionViewRunEmailListAction(tests.OnTaskTestCase):
    """Test the view to run actio item filter, json and email."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'tests',
        'initial_workflow',
        'initial_workflow.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'BIOL1011'

    def _verify_content(self):
        """Verify the content of the messages received."""
        self.assertTrue(
            mail.outbox[0].from_email == 'instructor01@bogus.com'
            and mail.outbox[0].subject == 'Email to instructor'
            and 'The emails of those students that ' in mail.outbox[0].body
            and 'instructor02@bogus.com' in mail.outbox[0].cc
            and 'Email to instructor' in mail.outbox[0].subject
            and 'user01@bogus.com' in mail.outbox[0].cc
            and 'user02@bogus.com' in mail.outbox[0].cc
            and 'user03@bogus.com' in mail.outbox[0].bcc
            and 'user04@bogus.com' in mail.outbox[0].bcc)


    def test_run_action_email_no_filter(self):
        """Run sequence of request to send email list ."""
        self.client.login(email=self.user_email, password=self.user_pwd)
        action = self.workflow.actions.get(name='Send Email with list')

        # Step 1 invoke the form
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(action.id == payload['action_id'])
        self.assertTrue(
            payload['prev_url'] == reverse(
                'action:run',
                kwargs={'pk': action.id}))
        self.assertTrue(payload['post_url'] == reverse('action:run_done'))
        self.assertTrue('post_url' in payload.keys())
        self.assertTrue(status.is_success(resp.status_code))

        # Step 2 send POST
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'email_to': 'instructor02@bogus.com',
                'cc_email': 'user01@bogus.com user02@bogus.com',
                'bcc_email': 'user03@bogus.com user04@bogus.com',
                'subject': 'Email to instructor'})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(payload == {})
        self.assertTrue(len(mail.outbox) == 1)
        self.assertTrue(status.is_success(resp.status_code))


class ActionViewRunJSONAction(tests.OnTaskTestCase):
    """Test the view to run actio item filter, json and email."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'tests',
        'initial_workflow',
        'initial_workflow.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'BIOL1011'

    def _verify_content(self):
        """Verify the content of the messages received."""
        self.assertTrue(all(
            json_item['auth'] == 'Bearer fake token'
            for json_item in OnTaskSharedState.json_outbox))

    def test_run_json_action_no_filter(self):
        """Test JSON action using the filter execution."""
        OnTaskSharedState.json_outbox = None
        self.client.login(email=self.user_email, password=self.user_pwd)
        action = self.workflow.actions.get(name='Send JSON to remote server')
        column = action.workflow.columns.get(name='email')

        # Step 1 invoke the form
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(action.id == payload['action_id'])
        self.assertTrue(
            payload['prev_url'] == reverse(
                'action:run',
                kwargs={'pk': action.id}))
        self.assertTrue(payload['post_url'] == reverse('action:run_done'))
        self.assertTrue('post_url' in payload.keys())
        self.assertTrue(status.is_success(resp.status_code))

        # Step 2 send POST
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'item_column': column.pk,
                'token': 'fake token'})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(payload == {})
        self.assertTrue(
            len(OnTaskSharedState.json_outbox) == action.get_rows_selected())
        self._verify_content()
        self.assertTrue(status.is_success(resp.status_code))

    def test_json_action_with_filter(self):
        """Test JSON action without using the filter execution."""
        OnTaskSharedState.json_outbox = None
        self.client.login(email=self.user_email, password=self.user_pwd)
        action = self.workflow.actions.get(name='Send JSON to remote server')
        column = action.workflow.columns.get(name='email')
        exclude_values = ['pzaz8370@bogus.com', 'tdrv2640@bogus.com']

        # Step 1 invoke the form
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(action.id == payload['action_id'])
        self.assertTrue(
            payload['prev_url'] == reverse(
                'action:run',
                kwargs={'pk': action.id}))
        self.assertTrue(payload['post_url'] == reverse('action:run_done'))
        self.assertTrue('post_url' in payload.keys())
        self.assertTrue(status.is_success(resp.status_code))

        # Step 2 send POST
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'item_column': column.pk,
                'confirm_items': True,
                'token': 'fake token'})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(payload['confirm_items'])
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)

        # Load the Filter page with a GET
        resp = self.get_response(
            'action:item_filter',
            session_payload=payload)
        self.assertTrue(status.is_success(resp.status_code))

        # Emulate the filter page with a POST
        resp = self.get_response(
            'action:item_filter',
            method='POST',
            req_params={'exclude_values': exclude_values})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(payload['exclude_values'] == exclude_values)
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.url, payload['post_url'])

        # Emulate the redirection to run_done
        resp = self.get_response('action:run_done')
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(payload == {})
        self.assertTrue(
            len(OnTaskSharedState.json_outbox) == (
                action.get_rows_selected() - len(exclude_values)))
        self.assertTrue(status.is_success(resp.status_code))


class ActionViewRunJSONListAction(tests.OnTaskTestCase):
    """Test the view to run actio item filter, json and email."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'tests',
        'initial_workflow',
        'initial_workflow.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'BIOL1011'

    def test_run_json_list_action(self):
        """Test JSON action using the filter execution."""
        OnTaskSharedState.json_outbox = None
        self.client.login(email=self.user_email, password=self.user_pwd)
        action = self.workflow.actions.get(name='Send list through JSON')

        # Step 1 invoke the form
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(action.id == payload['action_id'])
        self.assertTrue(
            payload['prev_url'] == reverse(
                'action:run',
                kwargs={'pk': action.id}))
        self.assertTrue(payload['post_url'] == reverse('action:run_done'))
        self.assertTrue('post_url' in payload.keys())
        self.assertTrue(status.is_success(resp.status_code))

        # Step 2 send POST
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'token': 'fake token'})
        payload = SessionPayload.get_session_payload(self.last_request)
        self.assertTrue(payload == {})
        self.assertTrue(
            len(OnTaskSharedState.json_outbox) == 1)
        self.assertTrue(
            OnTaskSharedState.json_outbox[0]['auth'] == 'Bearer fake token')
        self.assertTrue(status.is_success(resp.status_code))


class ActionViewRunCanvasEmailAction(tests.OnTaskTestCase):
    """Test the view to run actio item filter, json and email."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'tests',
        'initial_workflow',
        'initial_workflow.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'BIOL1011'

    def test_run_canvas_email_action(self):
        """Test Canvas Email action execution."""
        action = self.workflow.actions.get(name='Initial motivation')
        column = action.workflow.columns.get(name='SID')
        resp = self.get_response('action:run', url_params={'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))

        # POST -> redirect to item filter
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'subject': 'Email subject',
                'item_column': column.pk,
                'target_url': 'Server one',
            },
            session_payload={
                'item_column': column.pk,
                'action_id': action.id,
                'target_url': 'Server one',
                'prev_url': reverse('action:run', kwargs={'pk': action.id}),
                'post_url': reverse('action:run_done'),
            })
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)

    def test_run_canvas_email_done(self):
        """Test last step of sending canvas emails."""
        user = get_user_model().objects.get(email=self.user_email)
        utoken = models.OAuthUserToken(
            user=user,
            instance_name='Server one',
            access_token='bogus token',
            refresh_token=r'not needed',
            valid_until=timezone.now() + timedelta(days=1000000),
        )
        utoken.save()

        action = self.workflow.actions.get(name='Initial motivation')
        column = action.workflow.columns.get(name='email')
        settings.EXECUTE_ACTION_JSON_TRANSFER = False

        # POST -> redirect to item filter
        resp = self.get_response(
            'action:run_done',
            method='POST',
            session_payload={
                'item_column': column.pk,
                'action_id': action.id,
                'target_url': 'Server one',
                'prev_url': reverse('action:run', kwargs={'pk': action.id}),
                'post_url': reverse('action:run_done'),
                'subject': 'Email subject',
                'export_wf': False})
        self.assertTrue(status.is_success(resp.status_code))


class ActionServe(tests.OnTaskTestCase):
    """Test the view to serve an action."""

    fixtures = ['simple_action']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'simple_action.sql',
    )

    user_email = 'student01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'wflow1'

    def test_serve_action(self):
        """Test the serve_action view."""
        action = self.workflow.actions.get(name='simple action')
        action.serve_enabled = True
        action.save()

        resp = self.get_response(
            'action:serve',
            {'action_id': action.id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue('Oct. 10, 2017, 10:03 p.m.' in str(resp.content))


class ActionServeSurvey(tests.OnTaskTestCase):
    """Test the view to serve a survey."""

    fixtures = ['simple_workflow_two_actions']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'simple_workflow_two_actions.sql',
    )

    user_email = 'student01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'wflow2'

    def test_serve_survey(self):
        """Test the serve_action view."""
        action = self.workflow.actions.get(name='Check registration')
        action.serve_enabled = True
        action.save()

        resp = self.get_response(
            'action:serve',
            {'action_id': action.id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue('id="action-row-datainput"' in str(resp.content))
        self.assertTrue('csrfmiddlewaretoken' in str(resp.content))
