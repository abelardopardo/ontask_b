# -*- coding: utf-8 -*-

"""Test the Workflow API."""
import os

from django.conf import settings
from django.shortcuts import reverse
from rest_framework.authtoken.models import Token

from ontask import models
import test


class WorkflowApiCreate(test.OnTaskApiTestCase):
    fixtures = ['simple_workflow']

    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'simple_workflow.sql'
    )

    def setUp(self):
        super().setUp()
        # Get the token for authentication and set credentials in client
        token = Token.objects.get(user__email='instructor01@bogus.com')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_workflow_list(self):
        # Get list of workflows
        response = self.client.get(reverse('workflow:api_workflows'))

        # There should be one workflow identical to the one in the DB
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        # Get the workflow and compare
        wflow_id = response.data['results'][0]['id']
        workflow = models.Workflow.objects.get(id=wflow_id)
        self.assertEqual(wflow_id, 1)
        self.compare_wflows(response.data['results'][0], workflow)

    def test_workflow_create(self):
        # Trying to create an existing wflow and detecting its duplication
        response = self.client.post(
            reverse('workflow:api_workflows'),
            {'name': test.wflow_name})

        # Message should flag the existence of the wflow
        self.assertIn('Workflow could not be created.',
            response.data.get('detail', ''))

        # Create a second one
        response = self.client.post(
            reverse('workflow:api_workflows'),
            {'name': test.wflow_name + '2', 'attributes': {'one': 'two'}},
            format='json')

        # Compare the workflows
        workflow = models.Workflow.objects.get(name=test.wflow_name + '2')
        self.compare_wflows(response.data, workflow)

    def test_workflow_no_post_on_update(self):
        # POST method is not allowed in this URL
        response = self.client.post(
            reverse(
                'workflow:api_rud',
                kwargs={'pk': 1}),
            {'name': test.wflow_name + '2'})

        # Verify that the method post is not allowed
        self.assertIn('Method "POST" not allowed', response.data['detail'])

    def test_workflow_update(self):
        # Run the update (PUT) method
        response = self.client.put(reverse('workflow:api_rud',
            kwargs={'pk': 1}),
            {'name': test.wflow_name + '2',
             'description_text': test.wflow_desc + '2',
             'attributes': {'k1': 'v1'}},
            format='json')

        # Get the workflow and verify
        wflow_id = response.data['id']
        workflow = models.Workflow.objects.get(id=wflow_id)
        self.assertEqual(workflow.name, test.wflow_name + '2')

    def test_workflow_delete(self):
        # Run the update delete
        self.client.delete(reverse('workflow:api_rud', kwargs={'pk': 1}))

        # Get the workflow and verify
        self.assertFalse(models.Workflow.objects.filter(pk=1).exists())
