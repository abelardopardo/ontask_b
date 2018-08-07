# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

HELP_URL = getattr(settings, 'ONTASK_HELP_URL', '')
MINUTE_STEP = getattr(settings, 'SCHEDULER_MINUTE_STEP', 15)

if 'siteprefs' in settings.INSTALLED_APPS:
    # Respect those users who doesn't have siteprefs installed.
    from siteprefs.toolbox import patch_locals, register_prefs, pref

    patch_locals()  # That's bootstrap.

    register_prefs(
        pref(HELP_URL,
             verbose_name=_('URL prefix to access the documentation in the '
                            'static area'),
             static=False,
             field=models.CharField(max_length=256, blank=True)),

        pref(MINUTE_STEP,
             verbose_name=_('Minute interval to program scheduled tasks'),
             static=False,
             field=models.IntegerField(blank=True)),
    )
