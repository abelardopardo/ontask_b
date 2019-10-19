# -*- coding: utf-8 -*-

"""Table storing oauth tokens."""

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class OAuthUserToken(models.Model):
    """Table to store the tokens to authenticate with OAuth.

    There must be a one-to-one correspondence with the user, an access token,
    and a refresh token.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_index=True,
        on_delete=models.CASCADE,
        null=False,
        # related_name='oauth2_token',
        blank=False)

    # Instance name taken from the configuration parameters. It allows users
    # to have more than one token (as long as they are from different canvas
    # instances
    instance_name = models.CharField(
        max_length=2048,
        blank=False)

    access_token = models.CharField(max_length=2048, blank=False)

    refresh_token = models.CharField(max_length=2048, blank=True)

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    modified = models.DateTimeField(auto_now=True, null=False)

    # Token valid until
    valid_until = models.DateTimeField(
        _('Token valid until'),
        blank=False,
        null=False,
        default=None)

    class Meta:
        """Define uniqueness and table name."""

        unique_together = ('user', 'instance_name')
