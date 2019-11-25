# -*- coding: utf-8 -*-


from django.contrib import admin

from ontask import models


@admin.register(models.Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created', 'name', 'workflow', 'payload')
