# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models

CONTENT_TYPES = getattr(settings, 'DATAOPS_CONTENT_TYPES', 
                        '["text/csv", "application/json"]')

MAX_UPLOAD_SIZE = getattr(settings, 'DATAOPS_MAX_UPLOAD_SIZE', 209715200)

if 'siteprefs' in settings.INSTALLED_APPS:
    # Respect those users who doesn't have siteprefs installed.
    from siteprefs.toolbox import patch_locals, register_prefs, pref, \
        pref_group

    patch_locals()  # That's bootstrap.

    register_prefs(
        pref(CONTENT_TYPES,
             verbose_name='Content types allowed in uploads',
             static=False,
             field=models.CharField(max_length=256, blank=True)),
        pref(MAX_UPLOAD_SIZE,
             verbose_name='Maximum size allowed in file uplaods',
             static=False,
             field=models.IntegerField(blank=True)),
    )
