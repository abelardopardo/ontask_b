# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OnTaskConfig(AppConfig):
    name = 'ontask'
    verbose_name = _('OnTask')

    def ready(self) -> None:
        # Needed so that the signal registration is done
        # noinspection PyUnresolvedReferences
        from ontask import signals
