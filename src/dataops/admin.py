# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib import admin

from .models import PluginRegistry


class PluginRegistryAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'filename',
                    'modified',
                    'name',
                    'description_txt',
                    'executed')


admin.site.register(PluginRegistry, PluginRegistryAdmin)
