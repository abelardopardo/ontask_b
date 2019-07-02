# -*- coding: utf-8 -*-

"""Test views to run actions."""

import os
import test
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from ontask.action.payloads import (
    CanvasEmailPayload, EmailPayload, JSONPayload
)
from ontask.oauth.models import OAuthUserToken


class ActionViewRunAction(test.OnTaskTestCase):
    """Test the view to run actio item filter, json and email."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
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
            session_payload=payload.get_store())
        self.assertTrue(status.is_success(resp.status_code))

        # POST
        resp = self.get_response(
            'action:item_filter',
            method='POST',
            req_params={
                'exclude_values': ['ctfh9946@bogus.com'],
            },
            session_payload=payload.get_store())
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.url, reverse('action:email_done'))


class ActionViewRunJSONAction(test.OnTaskTestCase):
    """Test the view to run actio item filter, json and email."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'initial_workflow',
        'initial_workflow.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'BIOL1011'

    def test_run_json_action(self):
        """Test JSON action execution."""
        action = self.workflow.actions.get(name='Send JSON to remote server')
        payload = JSONPayload({
            'item_column': 'email',
            'action_id': action.id,
            'prev_url': reverse('action:run', kwargs={'pk': action.id}),
            'post_url': reverse('action:json_done'),
        })

        resp = self.get_response('action:run', url_params={'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))

        # POST -> redirect to item filter
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'key_column': 'email',
                'token': 'xxx',
                'confirm_items': True},
            session_payload=payload.get_store())
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.url, reverse('action:item_filter'))

        # POST -> done
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'key_column': 'email',
                'token': 'xxx'},
            session_payload=payload.get_store())
        self.assertTrue(status.is_success(resp.status_code))


class ActionViewRunCanvasEmailAction(test.OnTaskTestCase):
    """Test the view to run actio item filter, json and email."""

    fixtures = ['initial_workflow']
    filename = os.path.join(
        settings.BASE_DIR(),
        'initial_workflow',
        'initial_workflow.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'BIOL1011'

    def test_run_canvas_email_action(self):
        """Test Canvas Email action execution."""
        action = self.workflow.actions.get(name='Initial motivation')
        payload = CanvasEmailPayload({
            'item_column': 'email',
            'action_id': action.id,
            'target_url': 'Server one',
            'prev_url': reverse('action:run', kwargs={'pk': action.id}),
            'post_url': reverse('action:canvas_email_done'),
        })

        resp = self.get_response('action:run', url_params={'pk': action.id})
        self.assertTrue(status.is_success(resp.status_code))

        # POST -> redirect to item filter
        resp = self.get_response(
            'action:run',
            url_params={'pk': action.id},
            method='POST',
            req_params={
                'subject': 'Email subject',
                'key_column': 'email',
                'target_url': 'Server one',
            },
            session_payload=payload.get_store())
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)

    def test_run_canvas_email_done(self):
        """Test last step of sending canvas emails."""
        user = get_user_model().objects.get(email=self.user_email)
        utoken = OAuthUserToken(
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
            method='POST',
            session_payload=payload.get_store())
        self.assertTrue(status.is_success(resp.status_code))


class ActionServe(test.OnTaskTestCase):
    """Test the view to serve an action."""

    fixtures = ['simple_action']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'action',
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

class ActionServeSurvey(test.OnTaskTestCase):
    """Test the view to serve a survey."""

    fixtures = ['simple_workflow_two_actions']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'action',
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
