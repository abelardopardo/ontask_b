# -*- coding: UTF-8 -*-#


from builtins import object
from rest_framework import serializers

from .models import Log


class LogSerializer(serializers.ModelSerializer):
    useremail = serializers.ReadOnlyField()

    class Meta(object):
        model = Log
        fields = ('useremail', 'created', 'name', 'workflow', 'payload')
        read_only_fields = ('useremail', 'created', 'name', 'workflow',
                            'payload')
