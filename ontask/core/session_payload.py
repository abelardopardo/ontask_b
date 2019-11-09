# -*- coding: utf-8 -*-

"""Classes to implement a payload with a dictionary."""

import collections
from typing import Dict, Optional

from django.contrib.sessions.backends.base import SessionBase

PAYLOAD_SESSION_DICTIONARY = '__ontask_session_payload__'


class SessionPayload(collections.MutableMapping):
    """Objects to store the information in a session."""

    @classmethod
    def flush(cls, session: SessionBase):
        """Remove the table from the session."""
        session.pop(PAYLOAD_SESSION_DICTIONARY, None)

    def __init__(self,
        session: Optional[SessionBase] = None,
        initial_values: Optional[Dict] =None,
    ):
        """Initialize the store with the given arguments."""
        super().__init__()
        self.__store = {}
        if session:
            in_session = session.get(PAYLOAD_SESSION_DICTIONARY)
            if in_session:
                self.__store = in_session

        if initial_values:
            self.__store.update(initial_values)
        if session:
            self.store_in_session(session)

    def __getitem__(self, key):
        """Get item from the store.

        :param key: For lookup
        :return: Value
        """
        return self.__store[self.__keytransform__(key)]

    def __setitem__(self, key, item_value):
        """Set the key/value pair.

        :param key: lookup
        :param item_value: to be set
        :return: Nothing
        """
        self.__store[self.__keytransform__(key)] = item_value

    def __delitem__(self, key):  # noqa: Z434
        """Delete an item."""
        del self.__store[self.__keytransform__(key)]  # noqa: Z420

    def __iter__(self):
        """Return iterator."""
        return iter(self.__store)

    def __len__(self):
        """Return length."""
        return len(self.__store)

    def __keytransform__(self, key):
        """Transform the key."""
        return key

    def get_store(self):
        """Return the store."""
        return self.__store

    def store_in_session(self, session: SessionBase):
        """Set the payload in the current session.

        :param session: Session object
        """
        session[PAYLOAD_SESSION_DICTIONARY] = self.__store
        session.save()
