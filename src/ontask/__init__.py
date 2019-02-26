# -*- coding: utf-8 -*-
"""
Basic functions and definitions used all over the platform.
"""


import json
import pytz

from django.utils.translation import ugettext_lazy as _
from django.conf import settings as ontask_settings

from ontask.celery import app as celery_app

__all__ = ['celery_app', 'OnTaskException', 'is_legal_name', 'fix_pctg_in_name',
           'OnTaskDataFrameNoKey', 'action_session_dictionary',
           'get_action_payload']

__version__ = 'B.4.0.1'

PERSONALIZED_TEXT = 'personalized_text'
PERSONALIZED_CANVAS_EMAIL = 'personalized_canvas_email'
PERSONALIZED_JSON = 'personalized_json'
SURVEY = 'survey'
TODO_LIST = 'todo_list'

ACTION_TYPES = [
    (PERSONALIZED_TEXT, _('Personalized text')),
    (PERSONALIZED_CANVAS_EMAIL, _('Personalized Canvas Email')),
    (SURVEY, _('Survey')),
    (PERSONALIZED_JSON, _('Personalized JSON')),
    (TODO_LIST, _('TODO List'))
]

# Dictionary to store in the session the data between forms.
action_session_dictionary = 'action_run_payload'

def diff(a, b):
    """
    Calculate the operation a - b for two lists
    :param a: First list
    :param b: Second list
    :return: Elements in first list that are not in the second list
    """
    second = set(b)
    return [x for x in a if x not in second]


def is_legal_name(val):
    """
    Function to check if a string is a valid column name, attribute name or
    condition name.

    These are the characters that have been found to be problematic with
    these names and the responsible for these anomalies:

    - " Provokes a db error when handling the templates due to the encoding
      produced by the text editor.

    - ' String delimiter, python messes around with it and it is too complex to
        handle all possible cases and translations.

    In principle, arbitrary combinations of the following symbols should be
    handle by OnTask::

      !#$%&()*+,-./:;<=>?@[\]^_`{|}~

    :param val: String with the column name
    :return: String with a message suggesting changes, or None if string correct

    """

    if "'" in val:
        return _("The symbol ' cannot be used in the column name.")

    if '"' in val:
        return _('The symbol " cannot be used in the column name.')

    return None


def fix_pctg_in_name(val):
    """
    Function that escapes a value for SQL processing (replacing % by double %%)
    :param val: Value to escape
    :return: Escaped value
    """
    return val.replace('%', '%%')


def is_json(text):
    try:
        _ = json.loads(text)
    except ValueError:
        return False
    return True


def get_action_payload(request):
    """
    Gets the payload from the current session
    :param request: Request object
    :return: request.session[session_dictionary_name] or None
    """

    return request.session.get(action_session_dictionary, None)

def simplify_datetime_str(dtime):
    return dtime.astimezone(
                    pytz.timezone(ontask_settings.TIME_ZONE)
                ).strftime('%Y-%m-%d %H:%M:%S %z')

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
    """
    Exception to raise when a data frame has no key column
    """
    pass


class OnTaskDataFrameHasDuplicatedColumns(OnTaskException):
    """
    Exception to raise when the column names are duplicated
    """
    pass
