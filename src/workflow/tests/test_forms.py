# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from workflow.forms import WorkflowForm


class SetupClass(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user1@bogus.com",
            password="user1",
            is_superuser=False,
            name='User1 User1',
            is_active=True,
            is_staff=True)
        self.user.save()


class WorkflowFormTest(TestCase):
    # Valid data
    def test_workflow_valid(self):
        form = WorkflowForm(data={'name': 'workflow1',
                                  'description_text': 'Fake description text'})

        self.assertTrue(form.is_valid())

    def test_workflow_invalid1(self):
        form = WorkflowForm(data={'description_text': 'Fake description text'})

        self.assertFalse(form.is_valid())

    def test_workflow_invalid2(self):
        name = '   name with white spaces   '
        form = WorkflowForm(
            data={
                'name': name,
                'description_text': 'Fake description text'})

        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data['name'] == name.strip())


class WorkflowTestCreateView(SetupClass):
    def test_home_view(self):
        user_login = self.client.login(email='user1@bogus.com',
                                       password='user1')
        self.assertTrue(user_login)

        response = self.client.get(reverse('workflow:index'))

        # Should redirect to a page with the profile (it is not staff).
        self.assertEqual(response.status_code, 302)
