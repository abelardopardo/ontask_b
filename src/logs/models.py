# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings

#
# Model to encode logs in OnTask
#

log_types = [
    'workflow_create',
    'workflow_update',
    'workflow_delete',
    'workflow_data_upload',
    'workflow_data_merge',
    'workflow_data_failedmerge',
    'workflow_data_flush',
    'workflow_attribute_create',
    'workflow_attribute_update',
    'workflow_attribute_delete',
    'action_create',
    'action_update',
    'action_delete',
    'action_email_sent',
    'action_email_notify',
    'action_served_execute',
    'condition_create',
    'condition_update',
    'condition_delete',
    'filter_create',
    'filter_update',
    'filter_delete',
    'login',
]


class Log(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    # Type of event logged see above
    name = models.CharField(max_length=256, blank=False)

    # JSON element with additional information
    payload = models.CharField(max_length=65536,
                               default='',
                               null=False,
                               blank=False)

    def __unicode__(self):
        return '%s %s %s %s' % (self.user,
                                self.created,
                                self.name,
                                self.payload)
