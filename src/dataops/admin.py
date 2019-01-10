# -*- coding: utf-8 -*-


from django.contrib import admin

from .models import PluginRegistry, SQLConnection


class PluginRegistryAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'filename',
                    'modified',
                    'name',
                    'description_txt',
                    'executed')


class SQLConnectionAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'description_txt',
                    'conn_type',
                    'conn_driver',
                    'db_user',
                    'db_password',
                    'db_host',
                    'db_port',
                    'db_name',
                    'db_table')

admin.site.register(PluginRegistry, PluginRegistryAdmin)
admin.site.register(SQLConnection, SQLConnectionAdmin)
