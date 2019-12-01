# -*- coding: utf-8 -*-

"""Profiles models."""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


class BaseProfile(models.Model):
    """Base profile to use as abstract class."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                primary_key=True)
    slug = models.UUIDField(default=uuid.uuid4, blank=True, editable=False)
    # Add more user profile fields here. Make sure they are nullable
    # or with default values
    picture = models.ImageField(_('Profile picture'),
                                upload_to='profile_pics/%Y-%m-%d/',
                                null=True,
                                blank=True)
    bio = models.CharField("Short Bio", max_length=200, blank=True, default='')
    email_verified = models.BooleanField(_("Email verified"), default=False)

    class Meta:
        """Define the class as abstract."""

        abstract = True


class Profile(BaseProfile):
    """Profile class."""

    def __str__(self) -> str:
        return _("{}'s profile").format(self.user)
