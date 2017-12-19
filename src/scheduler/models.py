# -*- coding: utf-8 -*-
"""
This model is to store process to execute in the platform at a certain time.
"""
from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from action.models import Action
from workflow.models import Column


class ScheduledAction(models.Model):
    """
    Abstract class to encode the fields common to all scheduled actions.
    The actions can be either executed (and still kept in the DB) or pending.
    The actions can be of different types and the differences are kept in a
    JSON object.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False)

    # Type of action scheduled:
    #
    # - email_send: Send email
    type = models.CharField(max_length=256, blank=False, null=False)

    # Time of creation
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    # Boolean saying of this entry is deleted
    deleted = models.BooleanField(
        default=False,
        null=False,
        blank=False)

    # Time of execution
    execute = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name='When to execute this action'
    )

    # Status of the entry (pending, running or done)
    status = models.IntegerField(verbose_name="Execution Status",
                                 name='status',
                                 choices=[(0, 'pending'),
                                          (1, 'running'),
                                          (2, 'done'),
                                          (3, 'done_error')],
                                 null=False,
                                 blank=False)

    # Status message to capture a message resulting from the execution
    message = models.TextField(null=False,
                               blank=True,
                               verbose_name='Execution message')

    class Meta:
        """
        This model is abstract because it will be extended for the different
        scheduled actions.
        """
        abstract = True


class ScheduledEmailAction(ScheduledAction):
    """
    Objects encoding the scheduling of a send email action

    @DynamicAttrs
    """
    # The action out to get the email
    action = models.ForeignKey(Action,
                               db_index=True,
                               null=False,
                               blank=False,
                               related_name='scheduled_actions')

    subject = models.CharField(
        max_length=2048,
        default='',
        blank=False,
        null=False,
        verbose_name='Email subject'
    )

    email_column = models.ForeignKey(
        Column,
        db_index=False,
        null=False,
        blank=False,
        verbose_name='Column containing the email address')

    # If a confirmation email is sent ot the instructor
    send_confirmation = models.BooleanField(
        default=False,
        verbose_name='Send you a confirmation email',
        null=False,
        blank=False)

    # If the email reading is tracked (produces events in the logs)
    track_read = models.BooleanField(
        default=False,
        verbose_name='Track if emails are read?',
        null=False,
        blank=False)

    # If a new column will be added to the table with tracking counts.
    add_column = models.BooleanField(
        default=False,
        verbose_name='Add a column with the number of email reads tracked',
        null=False,
        blank=False)
