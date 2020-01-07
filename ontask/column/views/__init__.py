# -*- coding: utf-8 -*-

"""Column views."""
from ontask.column.views.criterion_crud import (
    criterion_create, criterion_edit, criterion_insert, criterion_remove,
)
from ontask.column.views.crud import (
    column_clone, column_edit, create, delete, formula_column_add, question_add,
    random_column_add)
from ontask.column.views.index import index, index_ss
from ontask.column.views.ops import (
    column_move, column_move_bottom, column_move_top, column_restrict_values,
)
