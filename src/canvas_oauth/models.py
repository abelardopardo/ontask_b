# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class CanvasUserTokens(models.Model):
    """
    Table to store the tokens to authenticate with Canvas. There must be
    a one-to-one correspondence with the user, an access token, and a refresh
    token.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             db_index=True,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False)
   
    access_token = models.CharField(max_length=2048, blank=False)

    refresh_token = models.CharField(max_length=2048, blank=True)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    # Token valid until
    valid_until = models.DateTimeField(_('Token valid until'),
                                       blank=False,
                                       null=False,
                                       default=None)
