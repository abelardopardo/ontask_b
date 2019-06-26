# -*- coding: utf-8 -*-

"""Module containing the forms for manipulating actions and conditions."""

from ontask.action.forms.crud import (
    FIELD_PREFIX, SUFFIX_LENGTH, ActionDescriptionForm, ActionForm,
    ActionImportForm, ActionUpdateForm, ConditionForm, FilterForm,
)
from ontask.action.forms.edit import (
    EditActionOutForm, EnterActionIn, column_to_field
)
from ontask.action.forms.run import (
    CanvasEmailActionForm, EmailActionForm, EnableURLForm, JSONActionForm,
    JSONBasicActionForm, ValueExcludeForm, ZipActionForm,
)
