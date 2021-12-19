# -*- coding: utf-8 -*-

from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class PrivateMediaStorage(S3Boto3Storage):
    location = settings.MEDIA_LOCATION
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    default_acl = 'private'
    custom_domain = False
