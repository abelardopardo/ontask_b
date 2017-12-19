# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import ScheduledEmailAction


class ScheduledEmailActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'created', 'execute',
                    'status', 'action', 'subject', 'email_column',
                    'send_confirmation', 'track_read', 'add_column',
                    'message')

admin.site.register(ScheduledEmailAction, ScheduledEmailActionAdmin)