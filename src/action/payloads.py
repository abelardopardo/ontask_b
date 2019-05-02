# -*- coding: utf-8 -*-

"""Classes capturing the payloads used when running actions."""
import collections

from django.conf import settings as ontask_settings

action_session_dictionary = 'action_run_payload'


def get_action_payload(session):
    """Get the payload from the current session.

    :param session: Session object

    :return: request.session[session_dictionary_name] or None
    """
    return session.get(action_session_dictionary)


def get_action_info(session, payloadclass=None, action_info=None):
    """Check the value of action_info and if needed, fetch from request.

    :param session: HTTP session object

    :param payloadclass: class to use to create action_info if needed. If None,
    it not created.

    :param action_info: Potentially existing action_info

    :return: Existing or newly created one
    """
    if action_info is not None:
        # It already exists, so simply return
        return action_info

    action_info = session.get(action_session_dictionary)
    if not action_info:
        # No action_info object found in session, return None!
        return action_info

    return payloadclass(action_info)


class ActionPayload(collections.MutableMapping):
    """Objects to store the information required for action execution.

    Look at the subclasses in this file for the different varieties
    """

    fields = []

    def __init__(self, *args, **kwargs):
        """Initialize the store and store given arguments."""
        super().__init__()
        self.store = {}
        if args:
            self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        """Verify that the key is in the allowed fields.

        :param key: For lookup
        :return: Value
        """
        if ontask_settings.DEBUG:
            if key not in self.fields:
                raise Exception('Incorrect key lookup.')
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, item_value):
        """Verify that the key is in the allowed fields.

        :param key: lookup
        :param item_value: to be set
        :return: Nothing
        """
        if ontask_settings.DEBUG:
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
        'exclude_values',
        'prev_url',
        'post_url',
        'button_label',
        'valuerange',
        'step',
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
        'exclude_values',
        'prev_url',
        'post_url',
        'button_label',
        'valuerange',
        'step',
    ]
