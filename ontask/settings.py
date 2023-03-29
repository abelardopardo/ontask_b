# -*- coding: utf-8 -*-

"""Configuration options that are persistent and editable among executions."""
import os
import sys

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from siteprefs.toolbox import (patch_locals, pref, pref_group, register_prefs)

# NOTIFICATION EMAILS
# ------------------------------------------------------------------------------
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

OVERRIDE_FROM_ADDRESS = getattr(settings, 'EMAIL_OVERRIDE_FROM')

# UPLOADS
# ------------------------------------------------------------------------------
CONTENT_TYPES = getattr(
    settings,
    'DATAOPS_CONTENT_TYPES',
    '["text/csv", "application/json", "application/gzip"]')

MAX_UPLOAD_SIZE = getattr(settings, 'DATAOPS_MAX_UPLOAD_SIZE', 209715200)

# TRANSFORMATIONS AND MODELS
# ------------------------------------------------------------------------------
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

# LOGS
# ------------------------------------------------------------------------------
MAX_LOG_LIST_SIZE = getattr(settings, 'LOGS_MAX_LIST_SIZE', 200)

# MISCELLANEOUS
# ------------------------------------------------------------------------------
HELP_URL = getattr(settings, 'ONTASK_HELP_URL', '')

patch_locals()  # That's for bootstrapping.

register_prefs(
    pref_group(
        _('Emails'),
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
            pref(
                OVERRIDE_FROM_ADDRESS,
                verbose_name=_('"From": field in all outgoing emails'),
                static=False,
                field=models.CharField(max_length=1024))),
        static=False),
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
    pref_group(
        _('Miscellaneous'),
        (
            pref(
                HELP_URL,
                verbose_name=_(
                    'URL prefix to access the documentation'),
                static=False,
                field=models.CharField(max_length=256, blank=True)),
        ),
        static=False),
)
