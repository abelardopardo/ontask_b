"""Basic functions and definitions used all over the platform."""
from datetime import datetime
import logging
from typing import List, Optional

from django import conf
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from email_validator import validate_email
from psycopg2 import sql
import pytz

from ontask.celery import app as celery_app

__all__ = [
    'celery_app',
    'CELERY_LOGGER',
    'create_new_name',
    'entity_prefix',
    'is_legal_name',
    'is_correct_email',
    'get_incorrect_email',
    'LOGGER',
    'OnTaskDataFrameNoKey',
    'OnTaskDBIdentifier',
    'OnTaskEmptyWorkflow',
    'OnTaskException',
    'OnTaskServiceException',
    'OnTaskSharedState',
    'simplify_datetime_str']

__version__ = '10.0'

LOGGER = logging.getLogger('ontask')

CELERY_LOGGER = logging.getLogger('celery_execution')


class OnTaskDBIdentifier(sql.Identifier):
    """Class to manage the presence of % in SQL identifiers."""

    def __init__(self, *strings: str):
        """Replace % by %% in string."""
        if not strings:
            raise TypeError('Identifier cannot be empty')

        super().__init__(*[strval.replace('%', '%%') for strval in strings])


class OnTaskSharedState:
    """Global dictionary."""

    __shared_state = {}

    def __init__(self):
        """Stored the shared state as the dictionary."""
        self.__dict__ = self.__shared_state


class OnTaskException(Exception):
    """Generic class in OnTask for exceptions."""

    def __init__(self, message, value=0):
        """Store message and value."""
        super().__init__()
        self.message = message
        self.value = value

    def __str__(self):
        """Return exception message as string representation."""
        return repr(self.message)


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


class OnTaskServiceException(OnTaskException):
    """Exception to raise when there is a service error.

    Attributes:
        field name -- name of the field with the error
        message -- explanation of the error
        objects_to_delete -- List of objects to apply the delete method.

    """

    def __init__(self, *args, **kwargs):
        """Store the three fields."""
        self.field_name = kwargs.pop('field_name', None)
        self.objects_to_delete = kwargs.pop('to_delete', [])

        super().__init__(*args, **kwargs)

    def message_to_error(self, request):
        """Store the message as error in the given request."""
        messages.error(request, self.message)

    def delete(self):
        """Proceed to delete the objects if applicable."""
        for obj_item in self.objects_to_delete:
            obj_item.delete()

    def __str__(self):
        """Render as a string."""
        return self.message


def is_legal_name(strval: str) -> Optional[str]:
    """Check if a string is a valid column, attribute or condition name.

    These are the characters that have been found to be problematic with
    these names and the responsible for these anomalies:

    - \" Provokes a db error when handling the templates due to the encoding
      produced by the text editor.

    - ' String delimiter, python messes around with it, and it is too complex to
        handle all possible cases and translations.

    In principle, arbitrary combinations of the following symbols should be
    handle by OnTask::

      !#$%&()*+,-./:;<=>?@[\\]^_`{|}~

    Additionally, any column name that starts with __ is reserved for OnTask.

    :param strval: String with the column name
    :return: String with message suggesting changes, or None if string correct
    """
    if "'" in strval:
        return _("The symbol ' cannot be used in the name.")

    if '"' in strval:
        return _('The symbol " cannot be used in the name.')

    if strval.startswith('__'):
        return _('The name cannot start with "__"')

    return None


def entity_prefix() -> str:
    """Return the prefix to use when cloning objects."""
    return _('Copy of ')


def is_correct_email(email_txt: str) -> bool:
    """Check if string is a correct email address."""
    try:
        validate_email(email_txt)
    except (ValueError, AttributeError):
        return False

    return True


def get_incorrect_email(emails: List[str]) -> Optional[str]:
    """Get the first incorrect email from a list

    :param emails: List of strings with emails
    :return: The first one that is incorrect or None if all correct.
    """
    email_txt = None
    try:
        for email_txt in emails:
            validate_email(email_txt)
    except (ValueError, AttributeError):
        return email_txt

    return None


def simplify_datetime_str(dtime: datetime) -> str:
    """Transform datetime object into string."""
    if dtime is None:
        return ''
    return dtime.astimezone(
        pytz.timezone(conf.settings.TIME_ZONE),
    ).strftime('%Y-%m-%d %H:%M:%S %z')


def create_new_name(old_name: str, obj_manager) -> str:
    """Provide a new name that does not exist in current manager.

    :param old_name: Current name
    :param obj_manager: Query to use to filter by name
    :return: New name
    """
    # Get the new name appending as many times as needed the 'Copy of '
    new_name = old_name
    while obj_manager.filter(name=new_name).exists():
        new_name = entity_prefix() + new_name

    return new_name


def get_country_code(language_code: str) -> str:
    """Extract the country code from the language code."""
    return language_code[0:language_code.find('-')]


def get_version() -> str:
    """Return the version string."""
    return __version__
