# -*- coding: utf-8 -*-

from django.contrib import admin

from ontask import models


@admin.register(models.OAuthUserToken)
class OAuthUserTokenAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'instance_name',
        'access_token',
        'refresh_token',
        'created',
        'modified',
        'valid_until')
