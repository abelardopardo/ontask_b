# -*- coding: utf-8 -*-

"""Abstract model for connections."""
from typing import Dict

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ontask.models.basic import NameAndDescription
from ontask.models.logs import Log


class Connection(NameAndDescription):
    """Model representing a connection to a data source.

    @DynamicAttrs
    """

    # Boolean that enables the use of this connection to other users.
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Available to users?'),
        null=False,
        blank=False,
    )

    optional_fields = []

    @classmethod
    def get(cls, pk):
        """Get the object with the given PK. Must be overwritten."""
        raise NotImplementedError

    def __str__(self):
        """Render with name field."""
        return self.name

    def has_missing_fields(self) -> bool:
        """Check if the connection has any parameter missing"""
        return any(
            not bool(getattr(self, field_name))
            for field_name in self.optional_fields)

    def get_missing_fields(self, form_values: Dict) -> Dict:
        """Get the missing fields from the given form"""
        to_return = {}
        for fname in self.optional_fields:
            to_return[fname] = getattr(self, fname)
            if not to_return[fname]:
                to_return[fname] = form_values[fname]
        return to_return

    def get_display_dict(self) -> Dict:
        """Create dictionary with (verbose_name, value)"""
        return {
            self._meta.get_field(key.name).verbose_name.title():
                self.__dict__[key.name]
            for key in self._meta.get_fields()
            if key.name != 'id'}

    def log(self, user, operation_type: str, **kwargs) -> int:
        """Function to register an event."""
        return Log.objects.register(
            self,
            user,
            operation_type,
            None,
            kwargs)

    class Meta(object):
        """Define as abstract and the ordering criteria."""

        abstract = True
        ordering = ['name']
