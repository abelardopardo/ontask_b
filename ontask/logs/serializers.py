# -*- coding: UTF-8 -*-#

"""Serializer for the API."""

from builtins import object

from rest_framework import serializers

from .models import Log


class LogSerializer(serializers.ModelSerializer):
    """Serialize the logs for the API"""

    useremail = serializers.ReadOnlyField()

    class Meta(object):
        """Choose the model, fields and read_only."""
        model = Log

        fields = ('useremail', 'created', 'name', 'workflow', 'payload')

        read_only_fields = (
            'useremail',
            'created',
            'name',
            'workflow',
            'payload')
