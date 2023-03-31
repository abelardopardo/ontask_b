# -*- coding: utf-8 -*-

"""Module with all the views used related to actions."""
from ontask.action.views.action import (
    ActionIndexView, ActionCreateView, ActionUpdateView, ActionDeleteView,
    ActionEditView, ActionCloneView)
from ontask.action.views.edit_personalized import (
    add_attachment, remove_attachment, save_text, showurl)
from ontask.action.views.edit_rubric import edit_rubric_cell, edit_rubric_loas
from ontask.action.views.edit_survey import (
    edit_description, select_column_action, select_condition_for_question,
    shuffle_questions, toggle_question_change, unselect_column_action)
from ontask.action.views.import_export import action_import, export
from ontask.action.views.preview import (
    preview_next_all_false, preview_response)
from ontask.action.views.run import (
    action_zip_export, run_action, run_action_item_filter, run_done,
    run_survey_row, serve_action, serve_action_lti, show_survey_table_ss,
    survey_thanks, zip_action)
from ontask.action.views.timeline import ActionShowTimelineView
