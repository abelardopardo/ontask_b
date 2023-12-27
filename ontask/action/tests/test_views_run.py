"""Test views to run actions."""
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from ontask import (
    OnTaskSharedState, models, settings as ontask_settings, tests)
from ontask.core import session_ops


class ActionViewRunBasic(tests.InitialWorkflowFixture, tests.OnTaskTestCase):
    """Test the view to run email action with no filter."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    def _verify_content(self, from_email='instructor01@bogus.com'):
        """Verify the content of the messages received.

        :param from_email: String to verify is in from field
        :return: Nothing. Runs assertion
        """
        self.assertTrue(all(
            message.from_email == from_email
            and message.subject == 'message subject'
            and 'Here are the comments about ' in message.body
            and 'user01@bogus.com' in message.cc
            and 'user02@bogus.com' in message.cc
            and 'user03@bogus.com' in message.bcc
            and 'user04@bogus.com' in message.bcc
            for message in mail.outbox))

    def _verify_json_content(self):
        """Verify the content of the messages received."""
        self.assertTrue(all(
            json_item['auth'] == 'Bearer fake token'
            for json_item in OnTaskSharedState.json_outbox))


class ActionViewRunEmailActionNoFilter(ActionViewRunBasic):
    """Test the view to run email action with no filter."""

    def test(self):
        action = self.workflow.actions.get(name='Midterm comments')
        column = action.workflow.columns.get(name='email')

        # Step 1 invoke the form
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id})
        payload = session_ops.get_payload(self.last_request)
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
        payload = session_ops.get_payload(self.last_request)
        self.assertIsNone(payload)
        self.assertTrue(len(mail.outbox) == action.get_rows_selected())
        self._verify_content()
        self.assertTrue(status.is_success(resp.status_code))


class ActionViewRunEmailActionOverrideFrom(ActionViewRunBasic):
    """Test the view to run email action and override FROM."""

    def test(self):
        # Modify the database with a new value
        old_override_from = ontask_settings.OVERRIDE_FROM_ADDRESS
        override_from = 'override@bogus.com'
        ontask_settings.OVERRIDE_FROM_ADDRESS = override_from

        action = self.workflow.actions.get(name='Midterm comments')
        column = action.workflow.columns.get(name='email')

        # Step 1 invoke the form
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id})
        payload = session_ops.get_payload(self.last_request)
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
        payload = session_ops.get_payload(self.last_request)
        self.assertIsNone(payload)
        self.assertTrue(len(mail.outbox) == action.get_rows_selected())
        self._verify_content(from_email=override_from)
        self.assertTrue(status.is_success(resp.status_code))

        # Restore the default value
        ontask_settings.OVERRIDE_FROM_ADDRESS = old_override_from


class ActionViewRunEmailWithFilter(ActionViewRunBasic):
    """Test the view to run email action with an item filter."""

    def test(self):
        action = self.workflow.actions.get(name='Midterm comments')
        column = action.workflow.columns.get(name='email')
        exclude_values = ['pzaz8370@bogus.com', 'tdrv2640@bogus.com']

        # Step 1 invoke the form
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id})
        payload = session_ops.get_payload(self.last_request)
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
        payload = session_ops.get_payload(self.last_request)
        self.assertTrue(payload['confirm_items'])
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)

        # Load the Filter page with a GET
        resp = self.get_response(
            'action:item_filter',
            payload=payload)
        self.assertTrue(status.is_success(resp.status_code))

        # Emulate the filter page with a POST
        resp = self.get_response(
            'action:item_filter',
            method='POST',
            req_params={'exclude_values': exclude_values})
        payload = session_ops.get_payload(self.last_request)
        self.assertTrue(payload['exclude_values'] == exclude_values)
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.url, payload['post_url'])

        # Emulate the redirection to run_done
        resp = self.get_response('action:run_done')
        payload = session_ops.get_payload(self.last_request)
        self.assertIsNone(payload)
        self._verify_content()
        self.assertTrue(
            len(mail.outbox) == (
                action.get_rows_selected() - len(exclude_values)))
        self.assertTrue(status.is_success(resp.status_code))


class ActionViewRunEmailWithItemFilter(ActionViewRunBasic):
    """Test the view to run email action with an item filter."""

    def test(self):
        action = self.workflow.actions.get(name='Midterm comments')
        column = action.workflow.columns.get(name='email')
        payload = {
            'item_column': column.pk,
            'action_id': action.id,
            'button_label': 'Send',
            'value_range': 2,
            'step': 2,
            'prev_url': reverse('action:run', kwargs={'pk': action.id}),
            'post_url': reverse('action:run_done')}
        resp = self.get_response(
            'action:item_filter',
            payload=payload)
        self.assertTrue(status.is_success(resp.status_code))

        # POST
        resp = self.get_response(
            'action:item_filter',
            method='POST',
            req_params={
                'exclude_values': ['ctfh9946@bogus.com'],
            },
            payload=payload)
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.url, reverse('action:run_done'))


class ActionViewRunEmailReportAction(ActionViewRunBasic):
    """Test the view to run a report action."""

    # def _verify_outbox_content(self, from_email='instructor01@bogus.com'):
    #     """Verify the content of the messages received."""
    #     self.assertTrue(
    #         mail.outbox[0].from_email == from_email
    #         and mail.outbox[0].subject == 'Email to instructor'
    #         and 'The emails of those students that ' in mail.outbox[0].body
    #         and 'instructor02@bogus.com' in mail.outbox[0].cc
    #         and 'Email to instructor' in mail.outbox[0].subject
    #         and 'user01@bogus.com' in mail.outbox[0].cc
    #         and 'user02@bogus.com' in mail.outbox[0].cc
    #         and 'user03@bogus.com' in mail.outbox[0].bcc
    #         and 'user04@bogus.com' in mail.outbox[0].bcc)

    def test(self):
        action = self.workflow.actions.get(name='Send Email with report')

        # Step 1 invoke the form
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id})
        payload = session_ops.get_payload(self.last_request)
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
        payload = session_ops.get_payload(self.last_request)
        self.assertIsNone(payload)
        self.assertTrue(len(mail.outbox) == 1)
        self.assertTrue(status.is_success(resp.status_code))


class ActionViewRunJSONActionNoFilter(ActionViewRunBasic):
    """Test the view to run a JSON action with no filter."""

    def test(self):
        OnTaskSharedState.json_outbox = None
        action = self.workflow.actions.get(name='Send JSON to remote server')
        column = action.workflow.columns.get(name='email')

        # Step 1 invoke the form
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id})
        payload = session_ops.get_payload(self.last_request)
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
        payload = session_ops.get_payload(self.last_request)
        self.assertIsNone(payload)
        self.assertTrue(
            len(OnTaskSharedState.json_outbox) == action.get_rows_selected())
        self._verify_json_content()
        self.assertTrue(status.is_success(resp.status_code))


class ActionViewRunJSONActionWithFilter(ActionViewRunBasic):
    """Test the view to run a JSON action filtering elements."""

    def test(self):
        OnTaskSharedState.json_outbox = None
        action = self.workflow.actions.get(name='Send JSON to remote server')
        column = action.workflow.columns.get(name='email')
        exclude_values = ['pzaz8370@bogus.com', 'tdrv2640@bogus.com']

        # Step 1 invoke the form
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id})
        payload = session_ops.get_payload(self.last_request)
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
        payload = session_ops.get_payload(self.last_request)
        self.assertTrue(payload['confirm_items'])
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)

        # Load the Filter page with a GET
        resp = self.get_response(
            'action:item_filter',
            payload=payload)
        self.assertTrue(status.is_success(resp.status_code))

        # Emulate the filter page with a POST
        resp = self.get_response(
            'action:item_filter',
            method='POST',
            req_params={'exclude_values': exclude_values})
        payload = session_ops.get_payload(self.last_request)
        self.assertTrue(payload['exclude_values'] == exclude_values)
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.url, payload['post_url'])

        # Emulate the redirection to run_done
        resp = self.get_response('action:run_done')
        payload = session_ops.get_payload(self.last_request)
        self.assertIsNone(payload)
        self.assertTrue(
            len(OnTaskSharedState.json_outbox) == (
                action.get_rows_selected() - len(exclude_values)))
        self.assertTrue(status.is_success(resp.status_code))


class ActionViewRunJSONReportAction(ActionViewRunBasic):
    """Test the view to run a JSON report action."""

    def test(self):
        OnTaskSharedState.json_outbox = None
        action = self.workflow.actions.get(name='Send JSON report')

        # Step 1 invoke the form
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id})
        payload = session_ops.get_payload(self.last_request)
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
        payload = session_ops.get_payload(self.last_request)
        self.assertIsNone(payload)
        self.assertTrue(len(OnTaskSharedState.json_outbox) == 1)
        self.assertTrue(
            OnTaskSharedState.json_outbox[0]['auth'] == 'Bearer fake token')
        self.assertTrue(status.is_success(resp.status_code))


class ActionViewRunCanvasEmailAction(ActionViewRunBasic):
    """Test the view to run a Canvas email action."""

    def test(self):
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
            payload={
                'item_column': column.pk,
                'action_id': action.id,
                'target_url': 'Server one',
                'prev_url': reverse('action:run', kwargs={'pk': action.id}),
                'post_url': reverse('action:run_done'),
            })
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)


class ActionViewRunCanvasEmailDone(ActionViewRunBasic):
    """Test the view to run a Canvas email action DONE."""

    def test(self):
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
            payload={
                'item_column': column.pk,
                'operation_type': action.action_type,
                'action_id': action.id,
                'target_url': 'Server one',
                'prev_url': reverse('action:run', kwargs={'pk': action.id}),
                'post_url': reverse('action:run_done'),
                'subject': 'Email subject',
                'export_wf': False})
        self.assertTrue(status.is_success(resp.status_code))


class ActionServe(tests.SimpleActionFixture, tests.OnTaskTestCase):
    """Test the view to serve an action."""

    user_email = 'student01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):
        action = self.workflow.actions.get(name='simple action')
        action.serve_enabled = True
        action.save(update_fields=['serve_enabled'])

        resp = self.get_response(
            'action:serve_lti',
            req_params={'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue('Oct. 10, 2017, 10:03 p.m.' in str(resp.content))


class ActionServeSurvey(
    tests.SimpleWorkflowTwoActionsFixture,
    tests.OnTaskTestCase
):
    """Test the view to serve a survey."""

    user_email = 'student01@bogus.com'
    user_pwd = 'boguspwd'

    def test(self):
        action = self.workflow.actions.get(name='Check registration')
        action.serve_enabled = True
        action.save(update_fields=['serve_enabled'])

        resp = self.get_response(
            'action:serve_lti',
            req_params={'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))
        self.assertTrue('id="action-row-datainput"' in str(resp.content))
        self.assertTrue('csrfmiddlewaretoken' in str(resp.content))
