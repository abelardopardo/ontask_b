"""Module with all the views used related to actions."""
from ontask.action.views.action import (
    ActionCloneView, ActionCreateView, ActionDeleteView, ActionIndexView,
    ActionUpdateView, action_edit)
from ontask.action.views.edit_personalized import (
    ActionAddRemoveAttachmentView, ActionShowURLView)
from ontask.action.views.edit_rubric import ActionEditRubricCellView
from ontask.action.views.edit_survey import (
    ActionEditDescriptionView, ActionSelectColumnSurveyView,
    ActionSelectConditionQuestionView, ActionShuffleQuestionsView,
    ActionToggleQuestionChangeView, ActionUnselectColumnSurveyView)
from ontask.action.views.import_export import (
    ActionExportView, ActionImportView)
from ontask.action.views.preview import (
    ActionPreviewNextAllFalseView, ActionPreviewView)
from ontask.action.views.run import (
    ActionRunActionItemFilterView, action_run_zip,
    ActionShowSurveyTableSSView, ActionZipExportView,
    action_run_finish, action_run_initiate)
from ontask.action.views.serve import (
    ActionRunSurveyRowView, ActionServeActionBasicView,
    ActionServeActionLTIView)
from ontask.action.views.timeline import ActionShowTimelineView
