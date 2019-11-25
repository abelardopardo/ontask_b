# -*- coding: utf-8 -*-

import logging

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from ontask import models
from ontask.dataops.sql import delete_table

logger = logging.getLogger("project")


@receiver(pre_delete, sender=models.Workflow)
def delete_data_frame_table(sender, instance, **kwargs):
    if instance.has_table():
        delete_table(instance.get_data_frame_table_name())
