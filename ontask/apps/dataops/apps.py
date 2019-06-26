# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DataopsConfig(AppConfig):
    name = 'ontask.apps.dataops'
    verbose_name = _('Data Upload/Merge Operations')
