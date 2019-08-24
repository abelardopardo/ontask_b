# -*- coding: utf-8 -*-

"""Package with the OnTask models."""

from ontask.models.action import (
    Action, ActionColumnConditionTuple, Condition, var_use_res,
)
from ontask.models.plugin import Plugin
from ontask.models.sqlconnection import SQLConnection
from ontask.models.logs import Log
from ontask.models.oauth import OAuthUserToken
from ontask.models.profiles import Profile
from ontask.models.scheduler import ScheduledAction
from ontask.models.table import View
from ontask.models.user import OnTaskUser
from ontask.models.workflow import Workflow
from ontask.models.column import Column

CHAR_FIELD_MID_SIZE = 512
CHAR_FIELD_LONG_SIZE = 2048
