"""Factory handling the various Scheduled Item Producers."""
from datetime import datetime
from typing import Dict, Optional
from zoneinfo import ZoneInfo

from django import http
from django.conf import settings
from django.shortcuts import redirect
from django.utils.dateparse import parse_datetime
from django.views import generic

from ontask import core, models


class SchedulerCRUDFactory(core.FactoryBase):
    """Factory to store Views to manage scheduled operations.

    Producer stores a tuple with:
    - Class.as_view() for view processing
    - Class to execute other methods
    """

    def register_producer(self, operation_type: str, producer_item):
        """Register the given item that will handle the scheduling."""
        to_register = (producer_item.as_view(), producer_item)
        super().register_producer(operation_type, to_register)

        if (
            producer_item.operation_type != operation_type
            and producer_item.operation_type not in self._producers
        ):
            # If the item has different operation_type field than the given
            # operation type, register it with both (one is for creation,
            # the other is once created, for editing)
            super().register_producer(
                producer_item.operation_type,
                to_register)

    def crud_view(
        self,
        request: http.HttpRequest,
        operation_type: int,
        **kwargs
    ) -> http.HttpResponse:
        """Execute the corresponding view function.

        :param request: Http request being processed
        :param operation_type: Type of scheduled item being processed.
        :param kwargs: Dictionary with the following fields:
        - workflow: Workflow being processed
        - action: Optional action being considered
        - scheduled_item: previously scheduled operation
        - payload: Dictionary with the data for the ongoing operation
        - is_finish_request: Boolean stating if this is a GET request to
        finish a previous op
        :return: HttpResponse
        """
        try:
            # Invoke the corresponding view processor
            view_processor, __ = self._get_producer(operation_type)
            return view_processor(
                request,
                operation_type=operation_type,
                **kwargs)
        except ValueError:
            return redirect('home')

    def api_create_or_update(
        self,
        user,
        data_dict: Dict,
        s_item: Optional[models.ScheduledOperation] = None,
    ):
        """Execute the function to create/update a scheduled operation.

        :param user: User creating the operation
        :param data_dict: Dictionary with all the information required to
         manipulate the new object (including the operation_type)
        :param s_item: Optional existing object
        :return: created object
        """
        __, api_producer = self._get_producer(data_dict['operation_type'])

        return api_producer.create_or_update(user, data_dict, s_item)


SCHEDULE_CRUD_FACTORY = SchedulerCRUDFactory()


class ScheduledOperationUpdateBaseView(generic.UpdateView):
    """Base class for all the scheduled operation CRUD producers.

    Attribute operation_type is the value to store in the scheduled item
    and needs to be overwritten by subclasses.
    """

    operation_type: Optional[int] = None
    model = models.ScheduledOperation
    template_name = 'scheduler/edit.html'

    object = None  # Placeholder for the schedule operation item

    workflow = None  # Fetched from the preliminary step.
    action = None  # Only valid for action execution (not uploads)
    connection = None  # For SQL Upload operations
    scheduled_item = None  # When editing a previously scheduled op

    # Dictionary stored in the session for multi-page form filling
    op_payload = None

    is_finish_request = None  # Flagging if the request is the last step.

    @staticmethod
    def _create_payload(
        request: http.HttpRequest,
        **kwargs
    ) -> core.SessionPayload:
        """Create the session payload to carry through the operation.

        :param kwargs: key/value pairs for the call
        :return: Session payload object
        """
        raise NotImplementedError

    @staticmethod
    def create_or_update(
        user,
        data_dict: Dict,
        s_item: Optional[models.ScheduledOperation] = None,
    ) -> models.ScheduledOperation:
        """Create/update scheduled item with the information in data_dict

        :param user: User creating the element
        :param data_dict: Data dictionary with the required fields
        :param s_item: Existing element (or None)
        :return: Element created or updated in the DB
        """
        if not s_item:
            s_item = models.ScheduledOperation(
                user=user,
                operation_type=data_dict['operation_type'],
                workflow=data_dict.pop('workflow'),
                action=data_dict.pop('action', None))
        data_dict.pop('operation_type', None)

        # Update the other fields
        s_item.name = data_dict.pop('name')
        s_item.description_text = data_dict.pop('description_text')

        execute = data_dict.pop('execute', '')
        if isinstance(execute, str):
            execute = parse_datetime(execute)
        s_item.execute = execute

        s_item.frequency = data_dict.pop('frequency', '')

        execute_until = data_dict.pop('execute_until', '')
        if isinstance(execute_until, str):
            execute_until = parse_datetime(execute_until)
        s_item.execute_until = execute_until

        s_item.status = models.scheduler.STATUS_PENDING

        if 'payload' in data_dict:
            # Object is coming through the API
            s_item.payload = dict(data_dict['payload'])
        else:
            # Object is coming through the WEB interface
            s_item.payload = dict(data_dict)

        column = s_item.payload.get('item_column')
        if isinstance(column, str):
            column = s_item.workflow.columns.filter(name=column).first()
            s_item.payload['item_column'] = column.id

        s_item.save()

        return s_item

    def setup(self, request, *args, **kwargs):
        """Store various fields in view, not kwargs."""
        super().setup(request, *args, **kwargs)
        self.workflow = kwargs.get('workflow', None)
        self.action = kwargs.get('action', None)
        self.scheduled_item = kwargs.get('scheduled_item', None)
        if self.scheduled_item:
            self.object = self.scheduled_item
            self.action = self.scheduled_item.action
        self.connection = kwargs.pop('connection', None)
        if (
            not self.connection
                and self.scheduled_item
                and 'connection_id' in self.scheduled_item.payload
        ):
            self.connection = models.SQLConnection.objects.get(
                pk=self.scheduled_item.payload['connection_id'])
        self.op_payload = kwargs.get('payload', self._create_payload(request))
        self.is_finish_request = self.kwargs.get('is_finish_request', False)
        return

    def dispatch(self, request, *args, **kwargs):
        """If this is "finish" request, invoke the finish method."""
        if self.is_finish_request:
            return self.finish(request, self.op_payload)

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None) -> Optional[models.ScheduledOperation]:
        """Modify to use the view for Create and Update."""
        return self.scheduled_item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        frequency = self.op_payload.get('frequency')
        if not frequency:
            frequency = '0 5 * * 0'

        all_false_conditions = False
        if self.action:
            all_false_conditions = any(
                cond.selected_count == 0
                for cond in self.action.conditions.all())

        context.update({
            'now': datetime.now(ZoneInfo(settings.TIME_ZONE)),
            'payload': self.op_payload,
            'frequency': frequency,
            'value_range': range(2),
            'all_false_conditions': all_false_conditions})
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'workflow': self.workflow,
            'action': self.action,
            'connection': self.connection,
            'columns': self.workflow.columns.filter(is_key=True),
            'form_info': self.op_payload})
        return kwargs

    def finish(
        self,
        request: http.HttpRequest,
        payload: core.SessionPayload,
    ) -> Optional[http.HttpResponse]:
        """Finalize the creation of a scheduled operation.

        All required data is passed through the payload.

        :param request: Request object received
        it has to be extracted from the information in the payload.
        :param payload: Dictionary with all the required data coming from
        previous requests.
        :return: Http Response
        """
        del request
        return None
