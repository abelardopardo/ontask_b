# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class ActionConfig(AppConfig):
    name = 'action'
    verbose_name = _('Actions, Conditions, Filters, Emails')
