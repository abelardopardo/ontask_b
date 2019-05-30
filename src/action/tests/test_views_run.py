# -*- coding: utf-8 -*-

"""Test views to run actions"""

from datetime import timedelta
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from action.payloads import EmailPayload, JSONPayload, CanvasEmailPayload
from action.views import (
    run_action_item_filter, run_action,
    run_canvas_email_done,
)
from ontask_oauth.models import OnTaskOAuthUserTokens
import test


class ActionViewRunAction(test.OnTaskTestCase):
    """Test the view to select items in an action."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        '..',
        'initial_workflow',
        'initial_workflow.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'BIOL1011'

    def test_run_action_item_filter(self):
        """Test the view to filter items."""
        action = self.workflow.actions.get(name='Midterm comments')
        payload = EmailPayload({
            'item_column': 'email',
            'action_id': action.id,
            'prev_url': reverse('action:run', kwargs={'pk': action.id}),
            'post_url': reverse('action:email_done'),
        })
        resp = self.get_response(
            'action:item_filter',
            run_action_item_filter,
            session_payload=payload.get_store())
        self.assertEqual(resp.status_code, 200)

        # POST
        resp = self.get_response(
            'action:item_filter',
            run_action_item_filter,
            method='POST',
            session_payload=payload.get_store(),
            req_params={
                'exclude_values': ['ctfh9946@bogus.com'],
            }
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('action:email_done'))

    def test_run_json_action(self):
        """Test JSON action execution"""
        action = self.workflow.actions.get(name='Send JSON to remote server')
        payload = JSONPayload({
            'item_column': 'email',
            'action_id': action.id,
            'prev_url': reverse('action:run', kwargs={'pk': action.id}),
            'post_url': reverse('action:json_done'),
        })

        resp = self.get_response(
            'action:run',
            run_action,
            url_params={'pk': action.id})
        self.assertEqual(resp.status_code, 200)

        # POST -> redirect to item filter
        resp = self.get_response(
            'action:run',
            run_action,
            url_params={'pk': action.id},
            method='POST',
            session_payload=payload.get_store(),
            req_params={
                'key_column': 'email',
                'token': 'xxx',
                'confirm_items': True}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('action:item_filter'))

        # POST -> done
        resp = self.get_response(
            'action:run',
            run_action,
            url_params={'pk': action.id},
            method='POST',
            session_payload=payload.get_store(),
            req_params={
                'key_column': 'email',
                'token': 'xxx'}
        )
        self.assertEqual(resp.status_code, 200)

    def test_run_canvas_email_action(self):
        """Test Canvas Email action execution"""
        action = self.workflow.actions.get(name='Initial motivation')
        payload = CanvasEmailPayload({
            'item_column': 'email',
            'action_id': action.id,
            'target_url': 'Server one',
            'prev_url': reverse('action:run', kwargs={'pk': action.id}),
            'post_url': reverse('action:canvas_email_done'),
        })

        resp = self.get_response(
            'action:run',
            run_action,
            url_params={'pk': action.id})
        self.assertEqual(resp.status_code, 200)

        # POST -> redirect to item filter
        resp = self.get_response(
            'action:run',
            run_action,
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'subject': 'Email subject',
                'key_column': 'email',
                'target_url': 'Server one',
            },
            session_payload=payload.get_store(),
        )
        self.assertEqual(resp.status_code, 302)

    def test_run_canvas_email_done(self):
        """Test last step of sending canvas emails."""
        user = get_user_model().objects.get(email=self.user_email)
        utoken = OnTaskOAuthUserTokens(
            user=user,
            instance_name='Server one',
            access_token='bogus token',
            refresh_token=r'not needed',
            valid_until=timezone.now() + timedelta(days=1000000),
        )
        utoken.save()

        action = self.workflow.actions.get(name='Initial motivation')
        payload = CanvasEmailPayload({
            'item_column': 'email',
            'action_id': action.id,
            'target_url': 'Server one',
            'prev_url': reverse('action:run', kwargs={'pk': action.id}),
            'post_url': reverse('action:canvas_email_done'),
            'subject': 'Email subject',
            'export_wf': False,
        })
        settings.EXECUTE_ACTION_JSON_TRANSFER = False

        # POST -> redirect to item filter
        resp = self.get_response(
            'action:canvas_email_done',
            run_canvas_email_done,
            method='POST',
            session_payload=payload.get_store(),
        )
        self.assertEqual(resp.status_code, 200)
