# -*- coding: utf-8 -*-

"""Factory handling the various Scheduled Item Producers."""

from django.shortcuts import render


class SchedulerCRUDFactory:
    """Factory to manipulate a scheduled operation."""

    def __init__(self):
        """Initialize the set of _creators."""
        self._producers = {}

    def _get_creator(self, operation_type):
        """Get the creator for the tiven operation_type and args."""
        creator_obj = self._producers.get(operation_type)
        if not creator_obj:
            raise ValueError(operation_type)
        return creator_obj

    def register_producer(self, operation_type: str, saver_obj):
        """Register the given object that will perform the save operation."""
        if operation_type in self._producers:
            raise ValueError(operation_type)
        self._producers[operation_type] = saver_obj

        if operation_type == saver_obj.operation_type:
            return

        # If the object has different operation_type field than the given
        # operation type, register it with both (one is for creation, the other
        # is once created, for editing)
        self._producers[saver_obj.operation_type] = saver_obj

    def crud_process(self, operation_type, **kwargs):
        """Execute the corresponding process function.

        :param operation_type: Type of scheduled item being processed. If the
        type is RUN_ACTION, the method explands its type looking at the type of
        action (either as a parameter, or within the schedule_item)
        :param kwargs: Dictionary with the following fields:
        - request: HttpRequest that prompted the process
        - action: Optional field stating the action being considered
        - schedule_item: Item being processed (if it exists)
        - prev_url: String with the URL to "go back" in case there is an
          intermediate step
        :return: HttpResponse
        """
        try:
            return self._get_creator(operation_type).process(**kwargs)
        except ValueError:
            return render(kwargs.get('request'), 'base.html', {})

    def crud_finish(self, operation_type, **kwargs):
        """Execute the corresponding finish function.

        :param operation_type: Type of scheduled item being processed. If the
        type is RUN_ACTION, the method explands its type looking at the type
        of action (either as a parameter, or within the schedule_item)
        :param kwargs: Dictionary with the following fields:
        - request: HttpRequest that prompted the process
        - schedule_item: Item being processed (if it exists)
        - payload: Dictionary with all the additional fields for the request
        :return: HttpResponse
        """
        try:
            return self._get_creator(operation_type).finish(**kwargs)
        except ValueError:
            return render(kwargs.get('request'), 'base.html', {})


schedule_crud_factory = SchedulerCRUDFactory()
