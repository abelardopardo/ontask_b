# -*- coding: utf-8 -*-

"""Functions to run the different types of actions."""
from django import http
from django.shortcuts import render

from ontask import models


class ActionManagementFactory:
    """Factory to run actions."""

    def __init__(self):
        """Initialize the set of runners."""
        self._runners = {}

    def register_producer(self, action_type: str, runner_obj):
        """Register the given object that will run the action type."""
        if action_type in self._runners:
            raise ValueError(action_type)
        self._runners[action_type] = runner_obj

    def process_edit_request(
        self,
        request: http.HttpRequest,
        workflow: models.Workflow,
        action: models.Action
    ) -> http.HttpResponse:
        """Execute the corresponding function to process an edit request.

        :param request: Http Request received (get or post)
        :param workflow: Workflow object being processed
        :param action: Action being edited
        :return: HttpResponse
        """
        try:
            runner_obj = self._runners.get(action.action_type)
            if not runner_obj:
                raise ValueError(action.action_type)
            return runner_obj.process_edit_request(
                request,
                workflow,
                action)
        except ValueError:
            return render(request, 'base.html', {})

    def process_run_request(self, action_type, **kwargs):
        """Execute the corresponding run function.

        :param action_type: Type of action being run.
        :param kwargs: Dictionary with additional required fields.
        :return: HttpResponse
        """
        try:
            runner_obj = self._runners.get(action_type)
            if not runner_obj:
                raise ValueError(action_type)
            return runner_obj.process_run_request(action_type, **kwargs)
        except ValueError:
            return render(kwargs.get('request'), 'base.html', {})

    def process_run_request_done(self, action_type: str, **kwargs):
        """Execute the corresponding function to finish a post request.

        :param action_type: Type of action being run.
        :param kwargs: Dictionary with additional required fields.
        :return: HttpResponse
        """
        try:
            runner_obj = self._runners.get(action_type)
            if not runner_obj:
                raise ValueError(action_type)
            return runner_obj.process_run_request_done(**kwargs)
        except ValueError:
            return render(kwargs.get('request'), 'base.html', {})


ACTION_PROCESS_FACTORY = ActionManagementFactory()
