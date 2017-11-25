# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf import settings
from django.db import models

EMAIL_HOST = getattr(settings, 'EMAIL_ACTION_EMAIL_HOST', '')
EMAIL_PORT = getattr(settings, 'EMAIL_ACTION_EMAIL_PORT', '')
EMAIL_HOST_USER = getattr(settings, 'EMAIL_ACTION_EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = getattr(settings, 'EMAIL_ACTION_EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = getattr(settings, 'EMAIL_ACTION_EMAIL_USE_TLS', '')
EMAIL_USE_SSL = getattr(settings, 'EMAIL_ACTION_EMAIL_USE_SSL', '')
NOTIFICATION_TEMPLATE = \
    getattr(settings,
            'EMAIL_ACTION_NOTIFICATION_TEMPLATE',
            """
<html>
<head/>
<body>
<p>Dear {{ user.name }}</p>

<p>This message is to inform you that on {{ email_sent_datetime }} a total of 
{{ num_messages }} emails were sent after the user {{ user.email }} executed 
the action with name  "{{ action.name }}".</p> 

{% if filter_present %}
<p>The action had a filter that reduced the number of messages from 
{{ num_rows }} to {{ num_selected }}.</p> 
{% else %}
<p>All the data rows stored in the workflow were used.</p>
{% endif %}

Regards.
The OnTask Support Team
</body></hrml>""")

NOTIFICATION_SUBJECT = getattr(settings,
                               'EMAIL_ACTION_NOTIFICATION_SUBJECT',
                               "OnTask: Action executed")

NOTIFICATION_SENDER = getattr(settings,
                              'EMAIL_ACTION_NOTIFICATION_SENDER',
                              'ontask@ontasklearning.org')

PIXEL = getattr(settings, 'EMAIL_ACTION_PIXEL', None)

if 'siteprefs' in settings.INSTALLED_APPS:
    # Respect those users who doesn't have siteprefs installed.
    from siteprefs.toolbox import patch_locals, register_prefs, pref, \
        pref_group

    patch_locals()  # That's bootstrap.

    register_prefs(
        pref_group(
            'SMTP Email Server Configuration',
            (pref(EMAIL_HOST,
                  verbose_name='Host name of the SMTP server',
                  static=False,
                  field=models.CharField(max_length=256, blank=True)),

             pref(EMAIL_PORT,
                  verbose_name='Host name of the SMTP server',
                  static=False,
                  field=models.CharField(max_length=256, blank=True)),

             pref(EMAIL_HOST_USER,
                  verbose_name='Username',
                  static=False,
                  field=models.CharField(max_length=256, blank=True)),

             pref(EMAIL_HOST_PASSWORD,
                  verbose_name='Password',
                  static=False,
                  field=models.CharField(max_length=256, blank=True)),

             pref(EMAIL_USE_TLS,
                  verbose_name='Use TLS?',
                  static=False,
                  field=models.CharField(max_length=256, blank=True)),

             pref(EMAIL_USE_SSL,
                  verbose_name='Use SSL?',
                  static=False,
                  field=models.CharField(max_length=256, blank=True)),
             ),
            static=False
        ),

        pref_group(
            'Notification Emails',
            (pref(NOTIFICATION_TEMPLATE,
                  verbose_name='Template to send email notification',
                  static=False,
                  field=models.TextField(max_length=65536)),
             pref(NOTIFICATION_SUBJECT,
                  verbose_name='Subject line for notification messages',
                  static=False,
                  field=models.CharField(max_length=1024)),
             pref(NOTIFICATION_SENDER,
                  verbose_name='To: field in notification emails',
                  static=False,
                  field=models.CharField(max_length=1024)),
             ),
            static=False
        ),
    )
