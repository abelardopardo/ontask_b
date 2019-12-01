# -*- coding: utf-8 -*-

"""Abstract model classes for common fields in mvarious objects."""

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

CHAR_FIELD_SMALL_SIZE = 512
CHAR_FIELD_MID_SIZE = 1024
CHAR_FIELD_LONG_SIZE = 2048


class Owner(models.Model):
    """Class containing the reference to the user owner."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_index=True,
        on_delete=models.CASCADE,
        null=False,
        blank=False)

    class Meta:
        """Define as abstract."""

        abstract = True


class NameAndDescription(models.Model):
    """Class containing the name and description of an object."""

    name = models.CharField(
        max_length=CHAR_FIELD_MID_SIZE,
        blank=False,
        verbose_name=_('name'),
    )

    description_text = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True,
        verbose_name=_('description'),
    )

    class Meta:
        """Define as abstract."""

        abstract = True


class CreateModifyFields(models.Model):
    """Class containing the created adn modified fields for an object."""

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        """Define as abstract."""

        abstract = True
