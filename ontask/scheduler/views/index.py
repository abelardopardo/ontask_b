"""Index of scheduled operations."""

from django.views import generic

import settings.base
from ontask.connection.services import create_sql_connection_runtable
from ontask.core import UserIsInstructor, WorkflowView, session_ops
from ontask.scheduler import services
from ontask import models


class SchedulerViewAbstract(generic.TemplateView):
    """Abstract class for all scheduler views."""

    # Title to use in template
    title = None
    # Item name to use in the button to create a new item
    item_name = None

    def get(self, request, *args, **kwargs):
        # Reset object to carry action info throughout dialogs
        session_ops.flush_payload(request)
        return super().get(request, *args, **kwargs)

    class Meta:
        abstract = True


class SchedulerIndex(UserIsInstructor, WorkflowView, SchedulerViewAbstract):
    """Render the list of scheduled actions in the workflow."""

    wf_pf_related = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = services.ScheduleActionTable(
            self.workflow.scheduled_operations.all(),
            orderable=False)
        context['sqlconnection'] = models.SQLConnection.objects.filter(
            enabled=True).exists()
        context['canvasconnection'] = len(settings.base.CANVAS_INFO_DICT) > 0
        return context
#
#
# class SchedulerConnectionIndex(
#     UserIsInstructor,
#     WorkflowView,
#     SchedulerViewAbstract
# ):
#     """Show table of SQL connections for user to choose one."""
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['table'] = create_sql_connection_runtable(
#             'scheduler:sqlupload')
#         # To show text instructing user to select one connection.
#         context['select_sql_connection'] = True
#         return context
