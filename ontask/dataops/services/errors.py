"""Define Plugin instantiation exceptions."""
from ontask import OnTaskServiceException


class OnTasDataopsPluginInstantiationError(OnTaskServiceException):
    """Raised when an error appears when instantiating a plugin class."""
