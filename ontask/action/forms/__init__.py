# -*- coding: utf-8 -*-

"""Module containing the forms for manipulating actions and conditions."""
from ontask.action.forms.crud import (
    ActionDescriptionForm, ActionForm,
    ActionImportForm, ActionUpdateForm, ConditionForm, FilterForm,
    RubricCellForm, RubricLOAForm,
)
from ontask.action.forms.edit import EditActionOutForm, EnterActionIn
from ontask.action.forms.run import (
    CanvasEmailActionForm,
    CanvasEmailActionRunForm, EmailActionForm, EmailActionRunForm,
    EnableURLForm, JSONActionForm, JSONActionRunForm, JSONListActionForm,
    JSONListActionRunForm, SendListActionForm, SendListActionRunForm,
    ValueExcludeForm, ZipActionRunForm,
)
