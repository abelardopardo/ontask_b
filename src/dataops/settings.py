# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import os
import sys

from django.conf import settings
from django.db import models


PLUGIN_DIRECTORY = getattr(settings,
                           'DATAOPS_PLUGIN_DIRECTORY',
                           os.path.join(settings.PROJECT_PATH,
                                        'plugins'))

# Get the plugin path in the sys.path
plugin_folder = PLUGIN_DIRECTORY
if not os.path.isabs(plugin_folder):
    plugin_folder = os.path.join(settings.PROJECT_PATH, plugin_folder)
if plugin_folder not in sys.path:
    sys.path.insert(0, plugin_folder)

if 'siteprefs' in settings.INSTALLED_APPS:
    # Respect those users who doesn't have siteprefs installed.
    from siteprefs.toolbox import (patch_locals, register_prefs, pref)

    patch_locals()  # That's bootstrap.

    register_prefs(
        pref(PLUGIN_DIRECTORY,
             verbose_name='Folder where plugins are stored',
             static=False,
             field=models.CharField(max_length=2048, blank=True)),
    )
