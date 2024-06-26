"""Abstract model for connections."""
from typing import Dict

from django.db import models
from django.utils.translation import gettext_lazy as _

from ontask.models.common import NameAndDescription
from ontask.models.logs import Log


class Connection(NameAndDescription):
    """Model representing a connection to a data source.

    @DynamicAttrs
    """

    # Boolean that enables the use of this connection to other users.
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled?'),
        null=False,
        blank=False)

    @classmethod
    def get(cls, primary_key):
        """Get the object with the given PK. Must be overwritten."""
        raise NotImplementedError

    def __str__(self):
        """Render with name field."""
        return self.name

    def get_display_dict(self) -> Dict:
        """Create dictionary with (verbose_name, value)"""
        return {
            self._meta.get_field(key.name).verbose_name.title():
                str(self.__dict__[key.name])
            for key in self._meta.get_fields()
            if key.name != 'id' and not isinstance(key, models.ForeignKey)}

    def log(self, user, operation_type: str, **kwargs) -> int:
        """Function to register an event."""
        return Log.objects.register(
            self,
            user,
            operation_type,
            None,
            kwargs)

    class Meta:
        """Define as abstract and the ordering criteria."""

        abstract = True
        ordering = ['name']
