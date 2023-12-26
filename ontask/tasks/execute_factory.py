"""Factory to execute the different operations."""
from typing import Any

from django.utils.translation import gettext_lazy as _

from ontask import core, OnTaskException


class TaskExecuteFactory(core.FactoryBase):
    """Factory to execute scheduled operations."""

    def execute_operation(self, operation_type, **kwargs) -> Any:
        """Execute the given operation.

        Invoke the object that implements the following method
        def execute_operation(
            self,
            user,
            workflow: Optional[models.Workflow] = None,
            action: Optional[models.Action] = None,
            payload: Optional[Dict] = None,
            log_item: Optional[models.Log] = None,
        ):

        :param operation_type: String encoding the type of operation
        :param kwargs: Parameters passed to execution
        :return: Whatever is returned by the execution
        """
        try:
            producer_cls = self._get_producer(operation_type)
        except ValueError:
            raise OnTaskException(_('Invalid operation type in task factory.'))

        return producer_cls().execute_operation(**kwargs)
