"""Workflow views."""
from ontask.workflow.views.attribute import (
    WorkflowAttributeCreateView, WorkflowAttributeEditView,
    WorkflowAttributeDeleteView)
from ontask.workflow.views.import_export import (
    WorkflowActionExportView, WorkflowImportView, WorkflowExportDoneView)
from ontask.workflow.views.share import (
    WorkflowShareCreateView, WorkflowShareDeleteView)
from ontask.workflow.views.workflow_crud import (
    WorkflowCreateView, WorkflowIndexView, WorkflowCloneView,
    WorkflowDeleteView, WorkflowUpdateView)
from ontask.workflow.views.workflow_ops import (
    WorkflowFlushView, WorkflowStar, WorkflowOperationsView,
    WorkflowAssignLUserColumn)
