# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib import admin

from .models import RowView


class RowViewAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'description_text',
                    'filter')

admin.site.register(RowView, RowViewAdmin)
