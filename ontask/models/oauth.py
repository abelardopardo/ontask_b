"""Table storing oauth tokens."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from fernet_fields import EncryptedCharField

from ontask.models.common import Owner, CHAR_FIELD_LONG_SIZE


class OAuthUserToken(Owner):
    """Table to store the tokens to authenticate with OAuth.

    There must be a one-to-one correspondence with the user, an access token,
    and a refresh token.
    """

    # Instance name taken from the configuration parameters. It allows users
    # to have more than one token (as long as they are from different canvas
    # instances
    instance_name = models.CharField(
        max_length=2048,
        blank=False)

    access_token = EncryptedCharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        blank=False)

    refresh_token = EncryptedCharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        blank=True)

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
