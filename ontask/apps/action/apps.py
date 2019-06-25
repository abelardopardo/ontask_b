# -*- coding: utf-8 -*-

"""Application definition."""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ActionConfig(AppConfig):
    """Define AppConfig class."""

    name = 'action'
    verbose_name = _('Actions, Conditions, Filters, Emails')
