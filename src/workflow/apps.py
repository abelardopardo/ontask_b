# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class WorkflowConfig(AppConfig):
    name = 'workflow'
    verbose_name = _('Workflows')

    def ready(self):
        from . import signals  # noqa
