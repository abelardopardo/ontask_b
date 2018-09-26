# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from scheduler.models import ScheduledAction


class ScheduledEmailActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'created', 'execute',
                    'status', 'action', 'item_column', 'last_executed_log')

admin.site.register(ScheduledAction, ScheduledEmailActionAdmin)
