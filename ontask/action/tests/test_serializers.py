"""Test the views for the scheduler pages."""
from ontask import tests
from ontask.action.serializers import ActionSelfcontainedSerializer


class ActionTestSerializers(
    tests.SimpleWorkflowTwoActionsFixture,
    tests.OnTaskTestCase,
):
    """Test stat views."""

    user_email = 'instructor01@bogus.com'
    user_pwd = 'boguspwd'

    action_obj = {
        "filter": {
            "columns": [],
            "description_text": "",
            "_formula": {
                "not": False, "rules": [{
                    "id": "age-2",
                    "type": "double",
                    "field": "age-2",
                    "input": "number",
                    "value": "12",
                    "operator": "greater"}],
                "valid": True,
                "condition": "AND"},
            "selected_count": 2},
        "conditions": [
            {
                "columns": [],
                "name": "Registered",
                "description_text": "",
                "_formula": {
                    "not": False, "rules": [{
                        "id": "registered-2",
                        "type": "boolean",
                        "field": "registered-2",
                        "input": "radio", "value": "1",
                        "operator": "equal"}],
                    "valid": True,
                    "condition": "AND"},
                "selected_count": 1}],
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
        "text_content": "<p>Hi {{ name }}</p><p>ATT: "
                        + "{{ attribute name }}</p><p>COL: " +
                        "{{ registered-2 }}</p><p>{% if Registered %}"
                        + "Thank you for registering{% else %}"
                        + "Remember to register{% endif %}</p>",
        "target_url": "",
        "shuffle": False}

    def test(self):
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
        action_data.save(user=self.workflow.user, name='NEW ACTION')
        self.workflow.refresh_from_db()
        action = self.workflow.actions.get(name='NEW ACTION')
        self.assertEqual(action.is_out, True)
        self.assertEqual(
            action.description_text,
            self.action_obj['description_text'])
        self.assertEqual(
            action.conditions.count(),
            len(self.action_obj['conditions']))
