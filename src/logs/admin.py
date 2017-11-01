# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib import admin

from .models import Log


class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created', 'name', 'workflow', 'payload')


admin.site.register(Log, LogAdmin)
