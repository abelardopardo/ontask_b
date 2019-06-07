# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import OnTaskOAuthUserTokens


class OnTaskOAuthUserTokensAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'instance_name',
                    'access_token',
                    'refresh_token',
                    'created',
                    'modified',
                    'valid_until')


admin.site.register(OnTaskOAuthUserTokens, OnTaskOAuthUserTokensAdmin)
