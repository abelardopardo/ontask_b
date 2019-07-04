# -*- coding: utf-8 -*-

"""Model extending the information to store in the user."""

from django.contrib.auth import get_user_model
from django.db import models


class OnTaskUser(models.Model):
    """Extend the existing authtools.User with additional fields."""

    # OneToOne relationship with the authentication model
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='ontask_info',
        primary_key=True,
    )

    def __str__(self):
        """Provide string representation (email)."""
        return self.user.email

    class Meta(object):
        """Additional attributes for the model."""

        verbose_name = 'ontaskuser'
        verbose_name_plural = 'ontaskusers'
