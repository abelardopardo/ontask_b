# -*- coding: utf-8 -*-

"""Exceptions when manipulating actions."""
from ontask import OnTaskServiceException


class OnTaskActionSurveyDataNotFound(OnTaskServiceException):
    """Raised when a survey is requested by a user but user is not found."""


class OnTaskActionSurveyNoTableData(OnTaskServiceException):
    """Raised when a survey requested by instructor has no data."""


class OnTaskActionRubricIncorrectContext(OnTaskServiceException):
    """Raised when a survey is requested by a user but user is not found."""
