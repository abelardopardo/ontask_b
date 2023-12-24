"""Factory to schedule execution of the different action types."""
from typing import Dict, List, Optional

from django import http
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext
from django.views import generic

from ontask import core, models, tasks
from ontask.core import session_ops


class ActionRunFactory(core.FactoryBase):
    """Factory to manage scheduling of action runs.

    Producer stores a tuple with:
    - Class.as_view() for view processing
    - Class to execute other methods
    """

    def process_request(
            self,
            request: http.HttpRequest,
            operation_type: int,
            **kwargs
    ) -> http.HttpResponse:
        """Execute function to process a run request.

        :param request: Http Request received (get or post)
        :param operation_type: Type of action being run.
        :param kwargs: Dictionary with action
        :return: HttpResponse
        """
        try:
            runner_view, __ = self._get_producer(operation_type)
        except ValueError:
            return redirect('home')

        return runner_view(request, operation_type=operation_type, **kwargs)

    def finish(self, action_type: str, **kwargs):
        """Execute the corresponding function to finish a post request.

        :param action_type: Type of action being run.
        :param kwargs: Dictionary with additional required fields.
        :return: HttpResponse
        """
        try:
            __, runner_cls = self._get_producer(action_type)
        except ValueError:
            return redirect('home')

        return runner_cls().finish(**kwargs)


ACTION_RUN_FACTORY = ActionRunFactory()


class ActionRunProducerBase(generic.FormView):
    """Base class for run view for the action"""

    workflow = None  # Fetched from the preliminary step.
    action = None  # Fetched from the preliminary step

    # Type of event to log when running the action
    log_event = None

    # Dictionary stored in the session for multipage form filling
    payload = None

    is_finish_request = None  # Flagging if the request is the last step.

    def _create_log_event(
            self,
            user,
            action: models.Action,
            payload: Optional[Dict] = None,
            log_item: Optional[models.Log] = None,
    ):
        """Create an ACTION RUN log if needed."""
        if log_item and not self.log_event:
            return log_item

        log_payload = dict(payload)
        log_payload['operation_type'] = self.log_event
        log_payload['action'] = action.name
        return action.log(user, **log_payload)

    @staticmethod
    def _update_excluded_items(payload: Dict, new_items: List[str]):
        """Update the list with exclude_items in the given payload

        :param payload: Dictionary being used for the execution
        :param new_items: List of new items to extend
        :result: Nothing. Payload is changed
        """
        exclude_values = payload.get('exclude_values', [])
        exclude_values.extend([str(x) for x in new_items])
        payload['exclude_values'] = exclude_values

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        self.workflow = kwargs.get('workflow', None)
        self.action = kwargs.get('action', None)

        self.payload = {
                'action_id': self.action.id,
                'operation_type': kwargs['operation_type'],
                'prev_url': kwargs.get('prev_url', None),
                'post_url': reverse('action:run_done')}
        # Store in session
        session_ops.set_payload(self.request, self.payload)

        self.is_finish_request = self.kwargs.get('is_finish_request', False)
        return

    def dispatch(self, request, *args, **kwargs):
        """If this is "finish" request, invoke the finish method."""
        if self.is_finish_request:
            return self.finish(request, self.workflow, self.payload)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'action': self.action,
            'num_msgs': self.action.get_rows_selected(),
            'all_false_conditions': any(
                cond.selected_count == 0
                for cond in self.action.conditions.all()),
            'value_range': range(2)})
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'columns': self.workflow.columns.all(),
            'action': self.action,
            'form_info': self.payload})
        return kwargs

    def form_valid(self, form) -> http.HttpResponse:
        """Process the VALID POST request."""
        if self.payload.get('confirm_items'):
            # Add information to the session object to execute the next pages
            self.payload['button_label'] = gettext('Send')
            self.payload['value_range'] = 2
            self.payload['step'] = 2

            return redirect('action:item_filter')

        # Go straight to the final step.
        return self.finish(self.request, self.workflow, self.payload)

    def finish(
            self,
            request: http.HttpRequest,
            workflow: models.Workflow,
            payload: dict,
    ) -> http.HttpResponse:
        """Finish processing the request after item selection."""
        # Get the information from the payload
        if not self.action:
            self.action = workflow.actions.filter(
                pk=payload['action_id']).first()
            if not self.action:
                return redirect('home')

        # Clean payload
        export_wf = payload.pop('export_wf', False)
        for payload_key in ['prev_url', 'post_url', 'confirm_items']:
            payload.pop(payload_key, None)

        log_item = self._create_log_event(request.user, self.action, payload)

        tasks.execute_operation.delay(
            self.log_event,
            user_id=request.user.id,
            log_id=log_item.id,
            workflow_id=workflow.id,
            action_id=self.action.id if self.action else None,
            payload=payload)

        # Reset object to carry action info throughout dialogs
        session_ops.flush_payload(request)

        # Successful processing.
        return render(
            request,
            'action/run_done.html',
            {'log_id': log_item.id, 'download': export_wf})

    def execute_operation(
            self,
            user,
            workflow: Optional[models.Workflow] = None,
            action: Optional[models.Action] = None,
            payload: Optional[Dict] = None,
            log_item: Optional[models.Log] = None,
    ):
        """Run the action."""
        del user, workflow, action, payload, log_item
        raise Exception('Incorrect invocation of run method.')
