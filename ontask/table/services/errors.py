"""Errors while executing table services."""
from ontask import OnTaskServiceException


class OnTaskTableNoKeyValueError(OnTaskServiceException):
    """Raised when receiving incorrect key/value pair."""


class OnTaskTableCloneError(OnTaskServiceException):
    """Raised when unable to clone."""
