# -*- coding: utf-8 -*-

"""Test the views for the scheduler pages."""

import os

from django.conf import settings

from ontask.action.serializers import ActionSelfcontainedSerializer
import test


class ActionTestSerializers(test.OnTaskTestCase):
    """Test stat views."""

    fixtures = ['simple_workflow_two_actions']
    filename = os.path.join(
        settings.BASE_DIR(),
        'ontask',
        'fixtures',
        'simple_workflow_two_actions.sql',
    )

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    workflow_name = 'wflow2'

    action_obj = {
        "conditions": [
            {
                "columns": [],
                "name": "old",
                "description_text": "",
                "formula": {
                    "not": False, "rules": [{
                        "id": "age",
                        "type": "double",
                        "field": "age",
                        "input": "number",
                        "value": "12",
                        "operator": "greater"}],
                    "valid": True,
                    "condition": "AND"},
                "n_rows_selected": 2,
                "is_filter": True},
            {
                "columns": [],
                "name": "Registered",
                "description_text": "",
                "formula": {
                    "not": False, "rules": [{
                        "id": "registered",
                        "type": "boolean",
                        "field": "registered",
                        "input": "radio", "value": "1",
                        "operator": "equal"}],
                    "valid": True,
                    "condition": "AND"},
                "n_rows_selected": 1,
                "is_filter": False}],
        "column_condition_pair": [],
        "is_out": True,
        "used_columns": [
            {
                "name": "age-2",
                "description_text": "",
                "data_type": "double",
                "is_key": False,
                "position": 1,
                "in_viz": True,
                "categories": [],
                "active_from": None,
                "active_to": None},
            {
                "name": "registered-2",
                "description_text": "",
                "data_type": "boolean",
                "is_key": False,
                "position": 5,
                "in_viz": True,
                "categories": [],
                "active_from": None,
                "active_to": None}],
        "name": "Detecting age",
        "description_text": "",
        "action_type": "personalized_text",
        "serve_enabled": False,
        "active_from": None,
        "active_to": None,
        "rows_all_False": [2],
        "text_content": "<p>Hi {{ name }}</p><p>ATT: {{ attribute name }}</p><p>COL: {{ registered }}</p><p>{% if Registered %}Thank you for registering{% else %}Remember to register{% endif %}</p>",
        "target_url": "", "shuffle": False}

    def test_serializer(self):
        """Test the self-contained action serializer."""
        # Try to create a view with a name that already exists.
        action_data = ActionSelfcontainedSerializer(
            data=self.action_obj,
            many=False,
            context={
                'user': self.workflow.user,
                'name': 'NEW ACTION',
                'workflow': self.workflow,
                'columns': self.workflow.columns.all()
            },
        )
        self.assertTrue(action_data.is_valid())
        action = action_data.save(user=self.workflow.user, name='NEW ACTION')
        self.workflow.refresh_from_db()
        action = self.workflow.actions.get(name='NEW ACTION')
        self.assertEqual(action.is_out, True)
        self.assertEqual(
            action.description_text,
            self.action_obj['description_text'])
        self.assertEqual(
            action.conditions.count(),
            len(self.action_obj['conditions']))
