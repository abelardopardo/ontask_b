# -*- coding: utf-8 -*-

"""Additional profile for OnTaskUsers."""
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

    def is_instructor(self) -> bool:
        """Return boolean with is_instructor answer."""
        return (
            self.user.is_authenticated
            and (
                self.user.groups.filter(name='instructor').exists()
                or self.user.is_superuser
            )
        )

    def __str__(self) -> str:
        """Provide string representation (email)."""
        return self.user.email

    class Meta:
        """Additional attributes for the model."""

        verbose_name = 'ontaskuser'
        verbose_name_plural = 'ontaskusers'
