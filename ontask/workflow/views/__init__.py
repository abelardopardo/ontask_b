# -*- coding: utf-8 -*-

"""Import view."""
from ontask.workflow.views.attribute import (
    attribute_create, attribute_delete, attribute_edit,
)
from ontask.workflow.views.column_crud import (
    column_add, column_clone, column_delete, column_edit, formula_column_add,
    random_column_add, question_add,
)
from ontask.workflow.views.column_ops import (
    column_move, column_move_bottom, column_move_top, column_restrict_values,
)
from ontask.workflow.views.criterion_crud import (
    criterion_create, criterion_edit, criterion_insert, criterion_remove,
)
from ontask.workflow.views.import_export import (
    export, export_ask, export_list_ask, import_workflow,
)
from ontask.workflow.views.share import share_create, share_delete
from ontask.workflow.views.workflow_crud import (
    WorkflowCreateView, clone_workflow, delete, detail, index, update,
)
from ontask.workflow.views.workflow_ops import (
    assign_luser_column, column_ss, flush, operations, star,
)
