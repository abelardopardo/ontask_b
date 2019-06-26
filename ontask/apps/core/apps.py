# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CoreConfig(AppConfig):
    name = 'ontask.apps.core'
    verbose_name = _('Core Configuration')

    def ready(self):
        # Needed so that the signal registration is done
        from . import signals  # noqa
