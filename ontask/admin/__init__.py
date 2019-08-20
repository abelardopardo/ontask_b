# -*- coding: utf-8 -*-

"""All admin classes for OnTask"""

from ontask.admin.profiles import UserProfileInline, NewUserAdmin
from ontask.admin.user import OnTaskUserAdmin
from ontask.admin.oauth import OAuthUserTokenAdmin
from ontask.admin.table import ViewAdmin
from ontask.admin.scheduler import ScheduledEmailActionAdmin
from ontask.admin.dataops import PluginRegistryAdmin, SQLConnectionAdmin
from ontask.admin.logs import LogAdmin
