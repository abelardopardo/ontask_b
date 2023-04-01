"""Functions and classes to flag invalid LTI request/config errors."""
from uuid import uuid1


def generate_identifier():
    """Return the uuid1 identifier."""
    return uuid1().__str__()


class InvalidLTIConfigError(Exception):
    def __init__(self, value):
        """Set the value."""
        self.value = value

    def __str__(self):
        """Return the string rendering."""
        return repr(self.value)


class InvalidLTIRequestError(Exception):
    def __init__(self, value):
        """Set the value."""
        self.value = value

    def __str__(self):
        """Return string rendering."""
        return repr(self.value)
