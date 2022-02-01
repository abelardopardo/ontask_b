"""Conventional factory functionality.

The platform currently uses four factories for the following functionality:

|---------------------+------+-----+----------+---------+
| Item/Operation      | Edit | Run | Schedule | Execute |
|---------------------+------+-----+----------+---------+
| Personalised email  |   X  |  X  |    X     |    X    |
| Email report        |   X  |  X  |    X     |    X    |
| Personalised rubric |   X  |  X  |    X     |    X    |
| Personalised JSON   |   X  |  X  |    X     |    X    |
| JSON report         |   X  |  X  |    X     |    X    |
| Canvas Email        |   X  |  X  |          |         |
| Zip                 |      |  X  |    -     |    -    |
| Survey              |   X  |  X  |    -     |    -    |
| TODO                |   ?  |  ?  |    -     |    -    |
| SQL upload          |      |     |    X     |    X    |
|---------------------+------+-----+----------+---------+
"""

from typing import Any


class FactoryBase:
    """Implement conventional factory methods."""

    def __init__(self):
        """Initialize the set of runners."""
        self._producers = {}

    def register_producer(self, operation_type: str, producer_item: Any):
        """Register the given item to process the requests."""
        if operation_type in self._producers:
            raise ValueError(operation_type)
        self._producers[operation_type] = producer_item

    def _get_producer(self, operation_type) -> Any:
        """Get the producer item for the given operation_type."""
        creator_obj = self._producers.get(operation_type)
        if not creator_obj:
            raise ValueError(operation_type)
        return creator_obj
