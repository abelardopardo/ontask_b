# -*- coding: utf-8 -*-

"""Factory handling the various Scheduled Item Producers."""
from datetime import datetime
from typing import Dict, Optional, Type

from django import forms, http
from django.conf import settings
from django.shortcuts import render
from django.utils.dateparse import parse_datetime
import pytz

from ontask import models
from ontask.core import SessionPayload


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

        :param operation_type: Type of scheduled item being processed.
        :param kwargs: Dictionary with the following fields:
        - request: HttpRequest that prompted the process
        - schedule_item: Item being processed (if it exists)
        - workflow: Optional workflow being processed
        - connection: Optional connection being processed
        - action: Optional action being considered
        - prev_url: Optional String with the URL to "go back" in case there is
        an intermediate step
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

    def crud_create_or_update(
        self,
        user,
        data_dict: Dict,
        s_item: Optional[models.ScheduledOperation] = None,
    ):
        """Execute the corresponding create/update function.

        :param user: User creating the operation
        :param data_dict: Dictionary with all the information required to
         manipulate the new object (including the operation_type)
        :param s_item: Optional existing object
        :return: created object
        """
        return self._get_creator(data_dict['operation_type']).create_or_update(
            user,
            data_dict,
            s_item)

schedule_crud_factory = SchedulerCRUDFactory()


class ScheduledOperationSaveBase:
    """Base class for all the scheduled operation CRUD producers.

    :Attribute operation_type: The value to store in the scheduled item
    and needs to be overwritten by subclasses

    :Attribute form_class: Form to be used when creating one operation in the
    Web interface.
    """

    operation_type: Optional[str] = None
    form_class: Type[forms.Form] = None

    @staticmethod
    def _create_payload(**kwargs) -> SessionPayload:
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
        """Create or update an object with the information in data_dict

        :param user: User creating the element
        :param data_dict: Data dictionary with the required fields
        :param s_item: Existing element (or None)
        :return: Nothing. Element created and inserted in the DB
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

        column = data_dict.pop('item_column', None)
        if isinstance(column, int):
            column = s_item.workflow.columns.filter(pk=column).first()
        s_item.item_column = column

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

        s_item.save()

        return s_item

    def process(
        self,
        request: http.HttpRequest,
        schedule_item: models.ScheduledOperation,
        workflow: Optional[models.Workflow] = None,
        connection: Optional[models.Connection] = None,
        action: Optional[models.Action] = None,
        prev_url: Optional[str] = None,
    ) -> http.HttpResponse:
        """Process the request."""
        if action:
            workflow = action.workflow

        op_payload = self._create_payload(
            request=request,
            operation_type=self.operation_type,
            schedule_item=schedule_item,
            workflow=workflow,
            connection=connection,
            action=action,
            prev_url=prev_url)

        form = self.form_class(
            form_data=request.POST or None,
            instance=schedule_item,
            workflow=workflow,
            connection=connection,
            action=action,
            columns=workflow.columns.filter(is_key=True),
            form_info=op_payload)
        if request.method == 'POST' and form.is_valid():
            return self.process_post(request, schedule_item, op_payload)

        frequency = op_payload.get('frequency')
        if not frequency:
            frequency = '0 5 * * 0'

        return render(
            request,
            'scheduler/edit.html',
            {
                'workflow': workflow,
                'action': action,
                'form': form,
                'now': datetime.now(pytz.timezone(settings.TIME_ZONE)),
                'frequency': frequency,
                'payload': op_payload})

    def process_post(
        self,
        request: http.HttpRequest,
        schedule_item: models.ScheduledOperation,
        op_payload: SessionPayload,
    ):
        """Process a POST request."""
        del request, schedule_item, op_payload
        raise ValueError('Incorrect  invocation of process_post method')

    def finish(
        self,
        request: http.HttpRequest,
        payload: SessionPayload,
        schedule_item: models.ScheduledOperation = None,
    ) -> Optional[http.HttpResponse]:
        """Finalize the creation of a scheduled operation.

        All required data is passed through the payload.

        :param request: Request object received
        :param schedule_item: ScheduledOperation item being processed. If None,
        it has to be extracted from the information in the payload.
        :param payload: Dictionary with all the required data coming from
        previous requests.
        :return: Http Response
        """
        del request, schedule_item, schedule_item
        return None
