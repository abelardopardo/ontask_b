# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models

PAGE_SIZE = getattr(settings, 'LOGS_PAGE_SIZE', 15)

if 'siteprefs' in settings.INSTALLED_APPS:
    # Respect those users who doesn't have siteprefs installed.
    from siteprefs.toolbox import patch_locals, register_prefs, pref, \
        pref_group

    patch_locals()  # That's bootstrap.

    register_prefs(
        pref(PAGE_SIZE,
             verbose_name='Number of logs per page',
             static=False,
             field=models.IntegerField(blank=True)),
    )
