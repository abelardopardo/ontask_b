# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ProfileConfig(AppConfig):
    name = "ontask.profiles"
    verbose_name = _('User Profiles')

    def ready(self):
        # Needed so that the signal registration is done
        from . import signals  # noqa
