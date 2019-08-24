# -*- coding: utf-8 -*-

"""All admin classes for OnTask"""

from ontask.admin.action import ActionAdmin
from ontask.admin.column import ColumnAdmin
from ontask.admin.condition import ConditionAdmin
from ontask.admin.logs import LogAdmin
from ontask.admin.oauth import OAuthUserTokenAdmin
from ontask.admin.plugin import PluginRegistryAdmin
from ontask.admin.profiles import NewUserAdmin, UserProfileInline
from ontask.admin.scheduler import ScheduledEmailActionAdmin
from ontask.admin.sqlconnection import SQLConnectionAdmin
from ontask.admin.user import OnTaskUserAdmin
from ontask.admin.view import ViewAdmin
from ontask.admin.workflow import WorkflowAdmin
