# -*- coding: utf-8 -*-

"""Amazon Athena Connection model."""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ontask.models.logs import Log
from ontask.models.const import CHAR_FIELD_LONG_SIZE, CHAR_FIELD_MID_SIZE


class AthenaConnection(models.Model):
    """Model representing a connection to an Amazon Athena data reposltory.

    @DynamicAttrs

    The parameters for the connection are those required to execute:

    conn = connect(aws_access_key_id='YOUR_ACCESS_KEY_ID',
               aws_secret_access_key='YOUR_SECRET_ACCESS_KEY',
               s3_staging_dir='s3://YOUR_S3_BUCKET/path/to/',
               region_name='us-west-2')
    df = pd.read_sql("SELECT * FROM many_rows", conn)

    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_S3_BUCKET_NAME
    AWS_S3_BUCKET_FILE_PATH
    AWS_REGION_NAME
    Table_name: The whole table is loaded.
    """

    # Connection name
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=CHAR_FIELD_LONG_SIZE,
        blank=False,
        unique=True)

    # Description
    description_text = models.CharField(
        verbose_name=_('Description'),
        max_length=CHAR_FIELD_LONG_SIZE,
        default='',
        blank=True)

    # Access key
    aws_access_key = models.CharField(
        verbose_name=_('AWS access key'),
        max_length=CHAR_FIELD_MID_SIZE,
        default='',
        null=False,
        blank=False)

    # Secret access key
    aws_secret_access_key = models.CharField(
        verbose_name=_('AWS secret access key'),
        max_length=CHAR_FIELD_MID_SIZE,
        default='',
        null=False,
        blank=False)

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
        null=False,
        blank=False)

    # AWS region name
    aws_region_name = models.CharField(
        verbose_name=_('AWS region name'),
        max_length=CHAR_FIELD_MID_SIZE,
        default='',
        null=False,
        blank=False)

    # DB table name
    table = models.CharField(
        max_length=CHAR_FIELD_LONG_SIZE,
        verbose_name=_('Table name'),
        default='',
        blank=False)

    def __str__(self):
        """Render with name field."""
        return self.name

    def log(self, user, operation_type: str, **kwargs):
        """Log the operation with the object."""
        payload = {
            'id': self.id,
            'name': self.name,
            'aws_access_key': self.aws_access_key,
            'aws_bucket_name': self.aws_bucket_name,
            'aws_file_path': self.aws_file_path,
            'aws_region_name': self.aws_region_name}

        if self.text_content:
            payload['content'] = self.text_content

        payload.update(kwargs)
        return Log.objects.register(user, operation_type, None, payload)

    class Meta:
        """Define the criteria for ordering."""

        ordering = ['name']
