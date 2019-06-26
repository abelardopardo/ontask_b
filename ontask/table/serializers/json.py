# -*- coding: utf-8 -*-

"""Serialize DataFrame related objects."""

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from ontask.table.serializers.merge import DataFrameJSONField


class DataFrameJSONSerializer(serializers.Serializer):
    """Serialize the data frame as a JSON object."""

    data_frame = DataFrameJSONField(
        help_text=_('JSON string encoding a pandas data frame'),
    )
