# -*- coding: utf-8 -*-

"""Classes to represent errors while executing services."""
from ontask import OnTaskServiceException


class OnTaskWorkflowStoreError(OnTaskServiceException):
    """Raised when an error appears in store_dataframe."""


class OnTaskWorkflowImportError(OnTaskServiceException):
    """Raised when an error appears in store_dataframe."""


class OnTaskWorkflowEmailError(OnTaskServiceException):
    """Raised when an error appears in store_dataframe."""
