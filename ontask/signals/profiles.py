# -*- coding: utf-8 -*-

"""Intercept a user creation and extend it with the profile."""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from ontask import models


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_handler(
    sender,
    instance,
    created: bool,
    **kwargs) -> None:
    """Create user profile if not created already."""
    del kwargs, sender
    if not created:
        return
    profile = models.Profile(user=instance)
    profile.save()
