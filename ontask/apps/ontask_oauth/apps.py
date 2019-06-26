# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OnTaskOauthConfig(AppConfig):
    name = 'ontask.apps.ontask_oauth'
    verbose_name = _('OnTask Oauth2 Authentication')
