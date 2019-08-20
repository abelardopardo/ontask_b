# -*- coding: utf-8 -*-

from django.contrib import admin

from ontask.models import OAuthUserToken


class OAuthUserTokenAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'instance_name',
        'access_token',
        'refresh_token',
        'created',
        'modified',
        'valid_until')


admin.site.register(OAuthUserToken, OAuthUserTokenAdmin)
