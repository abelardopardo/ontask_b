# -*- coding: UTF-8 -*-#
from __future__ import unicode_literals, print_function

from rest_framework import serializers

from .models import Log


class LogSerializer(serializers.ModelSerializer):
    useremail = serializers.ReadOnlyField()

    class Meta:
        model = Log
        fields = ('useremail', 'created', 'name', 'workflow', 'payload')
        read_only_fields = ('useremail', 'created', 'name', 'workflow',
                            'payload')
