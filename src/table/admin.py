# -*- coding: utf-8 -*-


from django.contrib import admin

from .models import View


class ViewAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'workflow',
                    'name',
                    'description_text',
                    'created',
                    'modified',
                    'formula')


# Register your models here.
admin.site.register(View, ViewAdmin)
