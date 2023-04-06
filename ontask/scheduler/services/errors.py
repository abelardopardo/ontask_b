"""Exceptions when manipulating scheduled items."""
from ontask import OnTaskServiceException


class OnTaskScheduleIncorrectTimes(OnTaskServiceException):
    """Raised when a schedule item has incorrect execute/until/freq."""
