# -*- coding: utf-8 -*-

"""Additional profile for OnTaskUsers."""

from django.contrib.auth import get_user_model
from django.db import models

from ontask.core.permissions import is_instructor


class OnTaskUser(models.Model):
    """Extend the existing authtools.User with additional fields."""

    # OneToOne relationship with the authentication model
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='ontask_info',
        primary_key=True,
    )

    def is_instructor(self) -> bool:
        """Return boolean with is_instructor answer."""
        return is_instructor(self.user)

    def __str__(self):
        """Provide string representation (email)."""
        return self.user.email

    class Meta(object):
        """Additional attributes for the model."""

        verbose_name = 'ontaskuser'
        verbose_name_plural = 'ontaskusers'
