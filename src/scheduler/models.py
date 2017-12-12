# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from workflow.models import Workflow


class ScheduledAction(models.Model):
    """
    Objects representing scheduled actions. The actions can be either
    executed (and still kept in the DB) or pending. The actions can be of
    different types and the differences are kept in a JSON object.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False)

    workflow = models.ForeignKey(Workflow,
                                 db_index=True,
                                 on_delete=models.CASCADE,
                                 null=False,
                                 blank=False,
                                 related_name='scheduled_actions')

    # Type of action scheduled:
    #
    # - email_send: Send email
    type = models.CharField(max_length=256, blank=False, null=False)

    # Time of creation
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    # Time of execution
    executed = models.DateTimeField(null=True)

    # Status of the entry (pending, running or done)
    status = models.IntegerField(verbose_name="Execution Status",
                                 name='status',
                                 choices=[(0, 'pending'),
                                          (1, 'running'),
                                          (2,'done')])

    # Field containing action specific fields
    payload = JSONField(default=dict, blank=False, null=False)