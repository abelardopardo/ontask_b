# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib import admin

from .models import CanvasUserTokens


class CanvasUserTokensAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'access_token',
                    'refresh_token',
                    'created',
                    'modified',
                    'valid_until')

admin.site.register(CanvasUserTokens, CanvasUserTokensAdmin)
