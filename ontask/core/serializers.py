# -*- coding: utf-8 -*-

"""Common serializer element for OnTask.

The purpose of this common element is to include the object id in the
serialization for purposes of recreating the object during import.
"""

import ontask
from rest_framework import serializers


class OnTaskVersionField(serializers.Field):
    """Define the version field for serialization."""

    def get_attribute(self, instance):
        return instance

    def to_representation(self, instance):
        """Return the object id."""
        return ontask.get_version()

    def to_internal_value(self, data):
        """Return the object id"""
        return data


class OnTaskObjectIdField(serializers.Field):
    """Define the object_id field for serialization."""

    def get_attribute(self, instance):
        return instance

    def to_representation(self, instance):
        """Return the object id."""
        return instance.id

    def to_internal_value(self, data):
        """Return the object id"""
        return data
