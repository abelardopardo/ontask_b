# -*- coding: utf-8 -*-


from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

NOTIFICATION_TEMPLATE = \
    getattr(settings,
            'EMAIL_ACTION_NOTIFICATION_TEMPLATE',
            """
<html>
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

NOTIFICATION_SUBJECT = getattr(settings,
                               'EMAIL_ACTION_NOTIFICATION_SUBJECT',
                               _("OnTask: Action executed"))

NOTIFICATION_SENDER = getattr(settings,
                              'EMAIL_ACTION_NOTIFICATION_SENDER',
                              'ontask@ontasklearning.org')

PIXEL = getattr(settings, 'EMAIL_ACTION_PIXEL', None)

if 'siteprefs' in settings.INSTALLED_APPS:
    # Respect those users who don't have siteprefs installed.
    from siteprefs.toolbox import patch_locals, register_prefs, pref, \
        pref_group

    patch_locals()  # That's bootstrap.

    register_prefs(
        pref_group(
            _('Notification Emails'),
            (pref(NOTIFICATION_TEMPLATE,
                  verbose_name=_('Template to send email notification'),
                  static=False,
                  field=models.TextField(max_length=65536)),
             pref(NOTIFICATION_SUBJECT,
                  verbose_name=_('Subject line for notification messages'),
                  static=False,
                  field=models.CharField(max_length=1024)),
             pref(NOTIFICATION_SENDER,
                  verbose_name=_('To: field in notification emails'),
                  static=False,
                  field=models.CharField(max_length=1024)),
             ),
            static=False
        ),
    )
