# -*- coding: utf-8 -*-

"""Create the user extension."""

import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from core import models

logger = logging.getLogger('project')


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_ontaskuser_handler(sender, instance, created, **kwargs):
    """Create the user extension whenever a new user is created."""
    if not created:
        return

    # Create the profile object, only if it is newly created
    ouser = models.OnTaskUser(user=instance)
    ouser.save()
    logger.info(
        _('New ontask user profile for {inst} created'),
        extra={'inst': instance})
