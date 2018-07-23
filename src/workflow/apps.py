# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class WorkflowConfig(AppConfig):
    name = 'workflow'
    verbose_name = _('Workflows')
