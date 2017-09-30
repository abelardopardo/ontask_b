# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Log


class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created', 'name', 'payload')


admin.site.register(Log, LogAdmin)
