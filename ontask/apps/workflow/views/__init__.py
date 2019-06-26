# -*- coding: utf-8 -*-

from ontask.apps.workflow.views.attribute import (
    attribute_create, attribute_delete, attribute_edit,
)
from ontask.apps.workflow.views.column_crud import (
    column_add, column_clone, column_delete, column_edit, formula_column_add,
    random_column_add,
)
from ontask.apps.workflow.views.column_ops import (
    column_move, column_move_bottom, column_move_top, column_restrict_values,
)
from ontask.apps.workflow.views.home import home
from ontask.apps.workflow.views.import_export import export, export_ask, import_workflow
from ontask.apps.workflow.views.share import share_create, share_delete
from ontask.apps.workflow.views.workflow_crud import (
    WorkflowCreateView, clone_workflow, delete, detail, index, update,
)
from ontask.apps.workflow.views.workflow_ops import (
    assign_luser_column, column_ss, flush, operations, star
)
