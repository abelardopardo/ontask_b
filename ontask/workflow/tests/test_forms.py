# -*- coding: utf-8 -*-

"""Test cases for the forms in the workflow package."""
from ontask import tests
import ontask.tests.basic
from ontask.workflow import forms


class WorkflowFormTest(ontask.tests.basic.OnTaskTestCase):
    # Valid data
    def test_workflow_valid(self):
        form = forms.WorkflowForm(
            data={
                'name': 'workflow1',
                'description_text': 'Fake description text'})

        self.assertTrue(form.is_valid())

    def test_workflow_invalid1(self):
        form = forms.WorkflowForm(
            data={'description_text': 'Fake description text'})

        self.assertFalse(form.is_valid())

    def test_workflow_invalid2(self):
        name = '   name with white spaces   '
        form = forms.WorkflowForm(
            data={
                'name': name,
                'description_text': 'Fake description text'})

        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data['name'] == name.strip())
