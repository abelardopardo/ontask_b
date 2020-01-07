# -*- coding: utf-8 -*-

"""Workflow views."""
from ontask.workflow.views.attribute import (
    attribute_create, attribute_delete, attribute_edit,
)
from ontask.workflow.views.import_export import (
    export, export_ask, export_list_ask, import_workflow,
)
from ontask.workflow.views.share import share_create, share_delete
from ontask.workflow.views.workflow_ops import (
    assign_luser_column, flush, operations, star,
)
