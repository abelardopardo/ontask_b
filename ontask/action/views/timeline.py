"""View to implement the timeline visualization."""

from django import http
from django.utils.translation import gettext_lazy as _
from django.views import generic

from ontask import models
from ontask.core import UserIsInstructor, WorkflowView


class ActionShowTimelineView(
    UserIsInstructor,
    WorkflowView,
    generic.TemplateView
):
    """Show the execution times of one/all actions."""

    template_name = 'action/timeline.html'
    single_action = False

    def get_context_data(self, **kwargs):
        """Get logs and action."""

        context = super().get_context_data(**kwargs)
        logs = self.workflow.logs
        if self.single_action:
            action = self.workflow.actions.filter(pk=kwargs.get('pk')).first()

            if not action:
                # The action is not part of the selected workflow
                raise http.Http404(_(
                    'Action does not belong to current workflow. '))
            context['action'] = action
            logs = logs.filter(payload__action_id=action.id)

        logs = logs.order_by('created')
        event_names = [
            models.Log.ACTION_DOWNLOAD,
            models.Log.ACTION_RUN_PERSONALIZED_CANVAS_EMAIL,
            models.Log.ACTION_RUN_PERSONALIZED_EMAIL,
            models.Log.ACTION_RUN_PERSONALIZED_JSON,
            models.Log.ACTION_RUN_JSON_REPORT,
            models.Log.ACTION_RUN_EMAIL_REPORT,
            models.Log.ACTION_SURVEY_INPUT,
            models.Log.SCHEDULE_CREATE,
            models.Log.SCHEDULE_EDIT,
            models.Log.SCHEDULE_DELETE]

        # Filter the logs to display and transform into values (process the
        # json and the long value for the log name
        context['event_list'] = logs.filter(name__in=event_names).exclude(
            payload__action=None)

        return context
