# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from models import ScheduledAction


class ScheduledActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'workflow', 'type', 'created', 'executed',
                    'status', 'payload')

admin.site.register(ScheduledAction, ScheduledActionAdmin)