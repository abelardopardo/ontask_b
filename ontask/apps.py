# -*- coding: utf-8 -*-
"""File defining the class with configuration operation"""
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OnTaskConfig(AppConfig):
    """Define app configuration."""
    name = 'ontask'
    verbose_name = _('OnTask')

    def ready(self) -> None:
        """Register the signals."""
        # Needed so that the signal registration is done
        # noinspection PyUnresolvedReferences
        from ontask import signals
