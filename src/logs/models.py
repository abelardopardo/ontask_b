# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings

from workflow.models import Workflow

#
# Model to encode logs in OnTask
#
class Log(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    # Type of event logged see above
    name = models.CharField(max_length=256, blank=False)

    workflow = models.ForeignKey(Workflow,
                                 db_index=True,
                                 on_delete=models.CASCADE,
                                 null=False,
                                 blank=False)

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
