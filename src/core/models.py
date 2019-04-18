# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models

class OnTaskUser(models.Model):
    """
    This model is to extend the existing authtools.User with additional fields
     relevant to OnTask
    """

    # OneToOne relationship with the authentication model
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='ontask_info',
        primary_key=True,
    )


