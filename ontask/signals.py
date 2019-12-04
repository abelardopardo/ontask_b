# -*- coding: utf-8 -*-

"""Intercept signals when manipulating some objects."""
import logging

from django.conf import settings
from django.db.models.signals import post_save, pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _

from ontask import models
from ontask.dataops.sql import delete_table

LOGGER = logging.getLogger('project')


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


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_ontaskuser_handler(sender, instance, created, **kwargs):
    """Create the user extension whenever a new user is created."""
    del sender, kwargs
    if not created:
        return

    # Create the profile object, only if it is newly created
    ouser = models.OnTaskUser(user=instance)
    ouser.save()
    LOGGER.info(_('New ontask user profile for %s created'), str(instance))


@receiver(pre_delete, sender=models.Workflow)
def delete_data_frame_table(sender, instance, **kwargs):
    """Delete the data table when deleting the workflow."""
    del sender, kwargs
    if instance.has_table():
        delete_table(instance.get_data_frame_table_name())
