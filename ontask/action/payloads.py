# -*- coding: utf-8 -*-

"""Classes capturing the payloads used when running actions."""

import collections
from typing import Dict, Mapping, Optional

from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase
from django.contrib.sessions.models import Session

PAYLOAD_SESSION_DICTIONARY = 'action_run_payload'


class ActionPayload(collections.MutableMapping):
    """Objects to store the information required for action execution.

    Look at the subclasses in this file for the different varieties
    """

    fields = []

    def __init__(self, initial_values=None):
        """Initialize the store and store given arguments."""
        super().__init__()
        self.store = {
            'exclude_values': [],
            'prev_url': '',
            'post_url': '',
            'button_label': '',
            'valuerange': 0,
            'step': 0,
        }

        if initial_values:
            self.update(initial_values)

    def __getitem__(self, key):
        """Verify that the key is in the allowed fields.

        :param key: For lookup
        :return: Value
        """
        if settings.DEBUG:
            if key not in self.fields:
                raise Exception('Incorrect key: ' + key)
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, item_value):
        """Verify that the key is in the allowed fields.

        :param key: lookup
        :param item_value: to be set
        :return: Nothing
        """
        if settings.DEBUG:
            if key not in self.fields:
                raise Exception('Incorrect key lookup.')

        self.store[self.__keytransform__(key)] = item_value

    def __delitem__(self, key):  # noqa: Z434
        """Delete an item."""
        del self.store[self.__keytransform__(key)]  # noqa: Z420

    def __iter__(self):
        """Return iterator."""
        return iter(self.store)

    def __len__(self):
        """Return length."""
        return len(self.store)

    def __keytransform__(self, key):
        """Transform the key."""
        return key

    def get_store(self):
        """Return the store."""
        return self.store


class EmailPayload(ActionPayload):
    """Objects to store the information required for email execution.

    Object to package the items required to carry out the email execution of an
    action. The object has the following fields:

    - action id: PK for the action being executed
    - subject: email subject
    - item_column: Name of the column that contains the target email addresses
    - cc_email: List of emails to include in the cc
    - bcc_email: List of emails to include in the bcc
    - confirm_items: Boolean encoding if a final item confirmation is needed
    - send_confirmation: Boolean encoding if a confirmation email is required
    - track_read: Boolean encoding if the email read is going to be tracked
    - export_wf: Boolean encoding if the workflow needs to be exported
    - exclude_values: Values in item_column that must be excluded
    - prev_url: URL to go back to the previous step in the process
    - post_url: URL to go next in the process
    - button_label: To use the right button label in the web page
    - valuerange: Range of steps considered
    - step: current step on that range
    """

    fields = [
        'action_id',
        'subject',
        'item_column',
        'cc_email',
        'bcc_email',
        'confirm_items',
        'send_confirmation',
        'track_read',
        'export_wf',
        'exclude_values',
        'prev_url',
        'post_url',
        'button_label',
        'valuerange',
        'step',
    ]


class SendListPayload(ActionPayload):
    """Objects to store the information required for send list execution.

    Object to package the items required to carry out the execution of an
    action of type send list. The object has the following fields:

    - action id: PK for the action being executed
    - subject: email subject
    - email_to: Destination email
    - cc_email: List of emails to include in the cc
    - bcc_email: List of emails to include in the bcc
    - export_wf: Boolean encoding if the workflow needs to be exported
    """

    fields = [
        'action_id',
        'subject',
        'email_to',
        'cc_email',
        'bcc_email',
        'export_wf',
    ]

class CanvasEmailPayload(ActionPayload):
    """Objects to store the information required for Canvas Email execution.

    Object to package the items required to carry out the JSON execution of an
    action. The object has the following fields:

    - action id: PK for the action being executed
    - prev_url: URL to go back to the previous step in the process
    - post_url: URL to go next in the process
    - button_label: To use the right button label in the web page
    - valuerange: Range of steps considered
    - step: current step on that range

    """

    fields = [
        'action_id',
        'subject',
        'item_column',
        'export_wf',
        'target_url',
        'confirm_items',
        'exclude_values',
        'prev_url',
        'post_url',
        'button_label',
        'valuerange',
        'step',
    ]

class JSONPayload(ActionPayload):
    """Objects to store the information required for JSON execution.

    Object to package the items required to carry out the JSON execution of an
    action. The object has the following fields:

    - action id: PK for the action being executed
    - token: for identification when making the request
    - item_column: Column that contains the value to personalize
    - exclude_values: Values in item_column that must be excluded
    - prev_url: URL to go back to the previous step in the process
    - post_url: URL to go next in the process
    - button_label: To use the right button label in the web page
    - valuerange: Range of steps considered
    - step: current step on that range

    """

    fields = [
        'action_id',
        'token',
        'item_column',
        'export_wf',
        'confirm_items',
        'exclude_values',
        'prev_url',
        'post_url',
        'button_label',
        'valuerange',
        'step',
    ]

class JSONListPayload(ActionPayload):
    """Object to store the information required for JSON List execution.

    Object to package the items required to carry out the execution of a JSON
    list action. The object has the following fields:

    - action id: PK for the action being executed
    - token: for identification when making the request
    - prev_url: URL to go back to the previous step in the process
    - post_url: URL to go next in the process
    - button_label: To use the right button label in the web page
    - valuerange: Range of steps considered
    - step: current step on that range

    """

    fields = [
        'action_id',
        'token',
        'item_column',
        'export_wf',
    ]

class ZipPayload(ActionPayload):
    """Objects to store the information required for JSON execution.

    Object to package the items required to carry out the ZIP execution of an
    action. The object has the following fields:

    - action id: PK for the action being executed
    - item_column: Column that contains the value to personalize
    - exclude_values: Values in item_column that must be excluded
    - prev_url: URL to go back to the previous step in the process
    - post_url: URL to go next in the process
    - button_label: To use the right button label in the web page
    - valuerange: Range of steps considered
    - step: current step on that range

    """

    fields = [
        'action_id',
        'item_column',
        'confirm_items',
        'exclude_values',
        'user_fname_column',
        'file_suffix',
        'zip_for_moodle',
        'prev_url',
        'post_url',
        'button_label',
        'valuerange',
        'step',
    ]

def get_action_payload(session: SessionBase) -> Dict:
    """Get the payload from the current session.

    :param session: Session object

    :return: request.session[session_dictionary_name] or None
    """
    return session.get(PAYLOAD_SESSION_DICTIONARY)

def set_action_payload(
    session: SessionBase,
    payload: Optional[Mapping] = None,
):
    """Set the payload in the current session.

    :param session: Session object

    :param payload: Dictionary to store
    """
    session[PAYLOAD_SESSION_DICTIONARY] = payload

def get_or_set_action_info(
    session: Session,
    payloadclass,
    action_info: Optional[ActionPayload] = None,
    initial_values: Optional[Dict] = None,
) -> Optional[ActionPayload]:
    """Get (from the session object) or create an ActionPayload object.

    First check if one is given. If not, check in the session. If there is no
    object in the session, create a new one with the initial values.

    :param session: HTTP session object

    :param payloadclass: class to use to create a action_info object.

    :param action_info: ActionInfo object just in case it is present.

    :param initial_values: A dictionary to initialize the class if required

    :return: Existing,newly created ActionInfo object, or None
    """
    if action_info:
        # Already exists, no need to create a new one
        return action_info

    action_info = session.get(PAYLOAD_SESSION_DICTIONARY)
    if action_info:
        return payloadclass(action_info)

    if not initial_values:
        # Nothing found in the session and no initial values given.
        return None

    # Create the object with the given class
    action_info = payloadclass(initial_values)
    session[PAYLOAD_SESSION_DICTIONARY] = action_info.get_store()
    session.save()

    return payloadclass(initial_values)
