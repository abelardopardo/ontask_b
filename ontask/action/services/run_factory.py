# -*- coding: utf-8 -*-

"""Functions to run the different types of actions."""

from django.shortcuts import render

from ontask import models
from ontask.action.services.email import ActionServiceRunEmail

class ActionRunRequestFactory(object):
    """Factory to run actions."""

    def __init__(self):
        """Initialize the set of runners."""
        self._runners = {}

    def register_runner(self, action_type: str, runner_obj):
        """Register the given object that will run the action type."""
        self._runners[action_type] = runner_obj

    def process_request(self, action_type, **kwargs):
        """Execute the corresponding run function.

        :param action_type: Type of action being run.
        :param kwargs: Dictionary with additional required fields.
        :return: HttpResponse
        """
        try:
            runner_obj = self._runners.get(action_type)
            if not runner_obj:
                raise ValueError(action_type)
            return runner_obj.process_request(action_type, **kwargs)
        except ValueError:
            return render(kwargs.get('request'), 'base.html', {})


    def process_done(self, action_type, **kwargs):
        """Execute the corresponding done function.

        :param action_type: Type of action being run.
        :param kwargs: Dictionary with additional required fields.
        :return: HttpResponse
        """
        try:
            runner_obj = self._runners.get(action_type)
            if not runner_obj:
                raise ValueError(action_type)
            return runner_obj.process_done(**kwargs)
        except ValueError:
            return render(kwargs.get('request'), 'base.html', {})

action_run_request_factory = ActionRunRequestFactory()
action_run_request_factory.register_runner(
    models.Action.PERSONALIZED_TEXT,
    ActionServiceRunEmail())
action_run_request_factory.register_runner(
    models.Action.RUBRIC_TEXT,
    ActionServiceRunEmail())
