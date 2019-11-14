# -*- coding: utf-8 -*-

"""All services for action manipulation."""

from ontask.action.services.canvas_email import ActionManagerCanvasEmail
from ontask.action.services.email import (
    ActionManagerEmail, ActionManagerEmailList,
)
from ontask.action.services.json import (
    ActionManagerJSON, ActionManagerJSONList,
)
from ontask.action.services.manager import ActionManagerBase
from ontask.action.services.manager_factory import (
    ActionManagementFactory, action_run_request_factory)
from ontask.action.services.serve_action import (
    serve_action_out, serve_survey_row,
)
from ontask.action.services.survey import (
    ActionManagerSurvey, create_survey_table,
)
from ontask.action.services.zip import ActionManagerZip, create_and_send_zip
