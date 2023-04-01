"""Module with all the views used related to actions."""
from ontask.action.views.action import (
    ActionCloneView, ActionCreateView, ActionDeleteView, ActionEditView,
    ActionIndexView, ActionUpdateView)
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
    ActionRunActionItemFilterView, ActionRunDoneView, ActionRunView,
    ActionRunZipView, ActionShowSurveyTableSSView, ActionZipExportView)
from ontask.action.views.serve import (
    ActionRunSurveyRowView, ActionServeActionLTIView,
    ActionServeActionBasicView)
from ontask.action.views.timeline import ActionShowTimelineView
