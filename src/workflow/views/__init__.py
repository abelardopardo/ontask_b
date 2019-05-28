# -*- coding: utf-8 -*-

from workflow.views.attribute import (
    attribute_create, attribute_delete, attribute_edit,
)
from workflow.views.clone import clone
from workflow.views.column_crud import (
    column_add, column_clone, column_delete, column_edit, formula_column_add,
    random_column_add,
)
from workflow.views.column_ops import (
    column_move, column_move_bottom, column_move_top, column_restrict_values,
)
from workflow.views.home import home
from workflow.views.import_export import export, export_ask, import_workflow
from workflow.views.share import share_create, share_delete
from workflow.views.workflow_crud import (
    WorkflowCreateView, delete, detail, index, update,
)
from workflow.views.workflow_ops import (
    assign_luser_column, column_ss, flush, operations,
)
