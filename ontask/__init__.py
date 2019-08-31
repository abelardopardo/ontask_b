# -*- coding: utf-8 -*-

"""Basic functions and definitions used all over the platform."""

import json

import django.conf
import pytz
from django.utils.translation import ugettext_lazy as _
from email_validator import validate_email
from psycopg2 import sql

from ontask.core.celery import app as celery_app

__all__ = [
    'celery_app', 'OnTaskException', 'is_legal_name',
    'OnTaskDataFrameNoKey', 'simplify_datetime_str', 'is_correct_email',
    'OnTaskEmptyWorkflow', 'OnTaskDBIdentifier', 'create_new_name',
    'OnTaskSharedState'
]

__version__ = 'B.5.2.2'

app_config = 'ontask.apps.ActionConfig'

PERSONALIZED_TEXT = 'personalized_text'
PERSONALIZED_CANVAS_EMAIL = 'personalized_canvas_email'
PERSONALIZED_JSON = 'personalized_json'
SEND_LIST = 'send_list'
SEND_LIST_JSON = 'send_list_json'
SURVEY = 'survey'
TODO_LIST = 'todo_list'

ACTION_TYPES = [
    (PERSONALIZED_TEXT, _('Personalized text')),
    (PERSONALIZED_CANVAS_EMAIL, _('Personalized Canvas Email')),
    (SURVEY, _('Survey')),
    (PERSONALIZED_JSON, _('Personalized JSON')),
    (SEND_LIST, _('Send List')),
    (SEND_LIST_JSON, _('Send List as JSON')),
    (TODO_LIST, _('TODO List'))
]

AVAILABLE_ACTION_TYPES = ACTION_TYPES[:]


def is_legal_name(val):
    """Check if a string is a valid column, attribute or condition name.

    These are the characters that have been found to be problematic with
    these names and the responsible for these anomalies:

    - " Provokes a db error when handling the templates due to the encoding
      produced by the text editor.

    - ' String delimiter, python messes around with it and it is too complex to
        handle all possible cases and translations.

    In principle, arbitrary combinations of the following symbols should be
    handle by OnTask::

      !#$%&()*+,-./:;<=>?@[\\]^_`{|}~

    Additionally, any column name that starts with __ is reserved for OnTask.

    :param val: String with the column name

    :return: String with a message suggesting changes, or None if string correct
    """
    if "'" in val:
        return _("The symbol ' cannot be used in the name.")

    if '"' in val:
        return _('The symbol " cannot be used in the name.')

    if val.startswith('__'):
        return _('The name cannot start with "__"')

    return None


def entity_prefix():
    """Return the prefix to use when cloning objects."""
    return _('Copy of ')


def is_correct_email(email_txt):
    try:
        validate_email(email_txt)
    except (ValueError, AttributeError):
        return False

    return True


def is_json(text):
    try:
        _ = json.loads(text)
    except ValueError:
        return False
    return True


def simplify_datetime_str(dtime):
    return dtime.astimezone(
        pytz.timezone(django.conf.settings.TIME_ZONE)
    ).strftime('%Y-%m-%d %H:%M:%S %z')


def create_new_name(old_name: str, obj_manager) -> str:
    """Provide a new name that does not exist in current manager

    :param old_name: Current name
    :param obj_manager: Query to use to filter by name
    :return: New name
    """
    # Get the new name appending as many times as needed the 'Copy of '
    new_name = old_name
    while obj_manager.filter(name=new_name).exists():
        new_name = entity_prefix() + new_name

    return new_name


class OnTaskDBIdentifier(sql.Identifier):
    """Class to manage the presence of % in SQL identifiers."""

    def __init__(self, *strings):
        if not strings:
            raise TypeError("Identifier cannot be empty")

        super().__init__(*[val.replace('%', '%%') for val in strings])


class OnTaskSharedState:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state


class OnTaskException(Exception):
    """
    Generic class in OnTask for our own exception
    """

    def __init__(self, msg, value=0):
        self.msg = msg
        self.value = value

    def __str__(self):
        return repr(self.msg)


class OnTaskDataFrameNoKey(OnTaskException):
    """Exception to raise when a data frame has no key column."""


class OnTaskDataFrameHasDuplicatedColumns(OnTaskException):
    """Exception to raise when the column names are duplicated."""


class OnTaskNoWorkflow(OnTaskException):
    """Exception to raise when there is no workflow."""


class OnTaskEmptyWorkflow(OnTaskException):
    """Exception to raise when the workflow has no table."""


class OnTaskNoAction(OnTaskException):
    """Exception to raise when there is no action."""
