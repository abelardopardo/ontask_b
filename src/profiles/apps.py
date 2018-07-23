from __future__ import unicode_literals
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class ProfileConfig(AppConfig):
    name = "profiles"
    verbose_name = _('User Profiles')

    def ready(self):
        from . import signals   # noqa
