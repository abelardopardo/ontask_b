# -*- coding: utf-8 -*-

"""All services for action manipulation."""
from ontask.action.services.action_table import ActionTable
from ontask.action.services.canvas_email import ActionManagerCanvasEmail
from ontask.action.services.clone import do_clone_action, do_clone_condition
from ontask.action.services.edit_save import save_action_form
from ontask.action.services.email import (
    ActionManagerEmail,
    ActionManagerEmailList,
)
from ontask.action.services.errors import (
    OnTaskActionSurveyDataNotFound,
    OnTaskActionSurveyNoTableData,
)
from ontask.action.services.json import ActionManagerJSON, ActionManagerJSONList
from ontask.action.services.manager import ActionRunManager
from ontask.action.services.manager_factory import (
    ActionManagementFactory,
    action_process_factory,
)
from ontask.action.services.preview import (
    create_list_preview_context,
    create_row_preview_context,
)
from ontask.action.services.rubric import ActionManagerRubric
from ontask.action.services.serve_action import (
    extract_survey_questions,
    get_survey_context, serve_action_out, update_row_values,
)
from ontask.action.services.survey import (
    ActionManagerSurvey,
    create_survey_table,
)
from ontask.action.services.zip import ActionManagerZip, create_and_send_zip
