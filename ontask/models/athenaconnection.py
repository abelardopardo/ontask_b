# -*- coding: utf-8 -*-

"""Amazon Athena Connection model."""
from typing import Dict

from django.db import models
from django.utils.translation import ugettext_lazy as _
from fernet_fields import EncryptedCharField, EncryptedTextField

from ontask.models.common import CHAR_FIELD_MID_SIZE
from ontask.models.connection import Connection
from ontask.models.logs import Log


class AthenaConnection(Connection):
    """Model representing a connection to an Amazon Athena data repository.

    @DynamicAttrs

    The parameters for the connection are those required to execute:

    cursor = connect(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        s3_staging_dir=staging_dir,
        region_name=region_name)

    df = pd.read_sql(
        'SELECT * FROM "bai-shared-curated".edx_grades_persistentcoursegrade',
        cursor)

    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY (OPTIONAL)
    AWS_SESSION_TOKEN [OPTIONAL]
    AWS_S3_BUCKET_NAME
    AWS_S3_BUCKET_FILE_PATH
    AWS_REGION_NAME

    No table name is stored to leave the possibility of choosing it at load
    time.
    """

    # Access key
    aws_access_key = models.CharField(
        verbose_name=_('AWS access key'),
        max_length=CHAR_FIELD_MID_SIZE,
        default='',
        null=False,
        blank=False)

    # Secret access key
    aws_secret_access_key = EncryptedCharField(
        verbose_name=_('AWS secret access key'),
        max_length=CHAR_FIELD_MID_SIZE,
        default='',
        null=True,
        blank=True,
        help_text=_('Leave blank to provide at execution'))

    # Secret access key
    aws_session_token = EncryptedTextField(
        verbose_name=_('AWS session token'),
        default='',
        null=True,
        blank=True,
        help_text=_('Leave blank to provide at execution'))

    # Bucket name
    aws_bucket_name = models.CharField(
        verbose_name=_('AWS S3 Bucket name (no s3:// prefix)'),
        max_length=CHAR_FIELD_MID_SIZE,
        default='',
        null=False,
        blank=False)

    # Bucket file path
    aws_file_path = models.CharField(
        verbose_name=_('AWS S3 Bucket file path'),
        max_length=CHAR_FIELD_MID_SIZE,
        default='',
        null=True,
        blank=True)

    # AWS region name
    aws_region_name = models.CharField(
        verbose_name=_('AWS region name'),
        max_length=CHAR_FIELD_MID_SIZE,
        default='',
        null=False,
        blank=False)

    # DB table (optional
    table_name = models.CharField(
        verbose_name=_('Table name'),
        max_length=CHAR_FIELD_MID_SIZE,
        default='',
        null=True,
        blank=True,
        help_text=_('Leave blank to provide at execution'))

    clone_event = Log.ATHENA_CONNECTION_CLONE
    create_event = Log.ATHENA_CONNECTION_CREATE
    delete_event = Log.ATHENA_CONNECTION_DELETE
    edit_event = Log.ATHENA_CONNECTION_EDIT
    toggle_event = Log.ATHENA_CONNECTION_TOGGLE

    optional_fields = [
        'aws_secret_access_key',
        'aws_session_token',
        'table_name']

    @classmethod
    def get(cls, pk):
        """Get the object with the given PK."""
        return AthenaConnection.objects.get(pk=pk)

    def get_display_dict(self) -> Dict:
        """Create dictionary with (verbose_name, value)"""
        d_dict = super().get_display_dict()
        remove_title = self._meta.get_field(
            'aws_secret_access_key').verbose_name.title()
        if remove_title in d_dict:
            d_dict[remove_title] = _('REMOVED')
        remove_title = self._meta.get_field(
            'aws_session_token').verbose_name.title()
        if remove_title in d_dict:
            d_dict[remove_title] = _('REMOVED')
        return d_dict

    def log(self, user, operation_type: str, **kwargs):
        """Log the operation with the object."""
        payload = {
            'id': self.id,
            'name': self.name,
            'aws_access_key': self.aws_access_key,
            'aws_bucket_name': self.aws_bucket_name,
            'aws_file_path': self.aws_file_path,
            'aws_region_name': self.aws_region_name,
            'table_name': self.table_name}

        payload.update(kwargs)
        return Log.objects.register(user, operation_type, None, payload)
