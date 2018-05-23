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
                    'num_column_input_from',
                    'num_column_input_to')


admin.site.register(PluginRegistry, PluginRegistryAdmin)
