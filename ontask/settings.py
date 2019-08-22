# -*- coding: utf-8 -*-

"""Basic configuration options."""

import os
import sys

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

############
#
# CORE
#
############
CONTENT_TYPES = getattr(
    settings,
    'DATAOPS_CONTENT_TYPES',
    '["text/csv", "application/json", "application/gzip"]')

HELP_URL = getattr(settings, 'ONTASK_HELP_URL', '')

MINUTE_STEP = getattr(settings, 'SCHEDULER_MINUTE_STEP', 15)

############
#
# LOGS
#
############
MAX_UPLOAD_SIZE = getattr(settings, 'DATAOPS_MAX_UPLOAD_SIZE', 209715200)
MAX_LOG_LIST_SIZE = getattr(settings, 'LOGS_MAX_LIST_SIZE', 200)

############
#
# ACTION
#
############
LONG_TEXT_FIELD_LENGTH = 65536

NOTIFICATION_TEMPLATE = getattr(
    settings,
    'EMAIL_ACTION_NOTIFICATION_TEMPLATE',
    """<html>
<head/>
<body>
<p>Dear {{ user.name }}</p>

<p>This message is to inform you that on {{ email_sent_datetime }}
{{ num_messages }} email{% if num_messages > 1 %}s{% endif %} were sent
resulting from the execution of the action with name "{{ action.name }}".</p>

{% if filter_present %}
<p>The action had a filter that reduced the number of messages from
{{ num_rows }} to {{ num_selected }}.</p>
{% else %}
<p>All the data rows stored in the workflow table were used.</p>
{% endif %}

Regards.
The OnTask Support Team
</body></html>""")

NOTIFICATION_SUBJECT = getattr(
    settings,
    'EMAIL_ACTION_NOTIFICATION_SUBJECT',
    _('OnTask: Action executed'))

NOTIFICATION_SENDER = getattr(
    settings,
    'EMAIL_ACTION_NOTIFICATION_SENDER',
    'ontask@ontasklearning.org')

PIXEL = getattr(settings, 'EMAIL_ACTION_PIXEL', None)

############
#
# DATAOPS
#
############
PLUGIN_DIRECTORY = getattr(
    settings,
    'DATAOPS_PLUGIN_DIRECTORY',
    os.path.join(settings.BASE_DIR, 'plugins'))

# Get the plugin path in the sys.path
plugin_folder = PLUGIN_DIRECTORY
if not os.path.isabs(plugin_folder):
    plugin_folder = os.path.join(settings.BASE_DIR, plugin_folder)
if plugin_folder not in sys.path:
    sys.path.insert(0, plugin_folder)

if 'siteprefs' in settings.INSTALLED_APPS:
    # Respect those users who doesn't have siteprefs installed.
    from siteprefs.toolbox import (
        patch_locals, register_prefs, pref, pref_group)

    patch_locals()  # That's bootstrap.

    register_prefs(
        ############
        #
        # Miscelaneous
        #
        ############
        pref_group(
            _('Miscelaneous'),
            (
                pref
                (HELP_URL,
                 verbose_name=_(
                     'URL prefix to access the documentation'),
                 static=False,
                 field=models.CharField(max_length=256, blank=True)),
                pref(
                    MINUTE_STEP,
                    verbose_name=_('Minute interval for scheduled tasks'),
                    static=False,
                    field=models.IntegerField(blank=True)),
            ),
            static=False),
        ############
        #
        # UPLOADS
        #
        ############
        pref_group(
            _('Uploads'),
            (
                pref(
                    CONTENT_TYPES,
                    verbose_name=_('Content types allowed in uploads'),
                    static=False,
                    field=models.TextField(blank=True)),
                pref(
                    MAX_UPLOAD_SIZE,
                    verbose_name=_('Maximum size allowed in file uplaods'),
                    static=False,
                    field=models.IntegerField(blank=True)),
            ),
            static=False),
        ############
        #
        # LOGS
        #
        ############
        pref_group(
            _('Logs'),
            (
                pref(
                    MAX_LOG_LIST_SIZE,
                    verbose_name=_('Maximum number of logs shown to the user'),
                    static=False,
                    field=models.IntegerField(blank=True)),
            ),
            static=False),
        ############
        #
        # ACTION
        #
        ############
        pref_group(
            _('Notification Emails'),
            (
                pref(
                    NOTIFICATION_TEMPLATE,
                    verbose_name=_('Template to send email notification'),
                    static=False,
                    field=models.TextField()),
                pref(
                    NOTIFICATION_SUBJECT,
                    verbose_name=_('Subject line for notification messages'),
                    static=False,
                    field=models.CharField(max_length=1024)),
                pref(
                    NOTIFICATION_SENDER,
                    verbose_name=_('"From:" field in notification emails'),
                    static=False,
                    field=models.CharField(max_length=1024)),
            ),
            static=False),
        ############
        #
        # DATAOPS
        #
        ############
        pref_group(
            _('Transformations and Models'),
            (
            pref(
                PLUGIN_DIRECTORY,
                verbose_name=_('Folder where code packages are stored'),
                static=False,
                field=models.CharField(max_length=2048, blank=True)),
            ),
            static=False),
    )
