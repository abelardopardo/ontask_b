# -*- coding: utf-8 -*-

"""Module with all the views used related to actions."""
from ontask.condition.views.clone import clone_condition
from ontask.condition.views.crud import (
    ConditionCreateView, ConditionDeleteView, ConditionUpdateView,
    FilterDeleteView, FilterSetView, FilterUpdateView)
