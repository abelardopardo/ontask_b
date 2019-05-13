# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import test
from workflow.forms import WorkflowForm


class WorkflowFormTest(test.OnTaskTestCase):
    # Valid data
    def test_workflow_valid(self):
        form = WorkflowForm(
            data={
                'name': 'workflow1',
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
