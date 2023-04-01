"""Classes to represent errors while executing services."""
from ontask import OnTaskServiceException


class OnTaskColumnAddError(OnTaskServiceException):
    """Raised when an error appears in store_dataframe."""


class OnTaskColumnCategoryValueError(OnTaskServiceException):
    """Raised when an error appears in store_dataframe."""


class OnTaskColumnIntegerLowerThanOneError(OnTaskServiceException):
    """Raised when an integer value incorrect."""
