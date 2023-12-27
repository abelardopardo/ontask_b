"""Service to create a SQL update operation."""
from django import http
from django.utils.translation import gettext, gettext_lazy as _

from ontask.scheduler.forms.basic import ScheduleSQLUploadForm
from ontask import models, OnTaskException
from ontask.scheduler.services.edit_factory import (
    ScheduledOperationUpdateBaseView)


class ScheduledOperationUpdateSQLUpload(ScheduledOperationUpdateBaseView):
    """Class to create a SQL Upload operation."""

    operation_type = models.Log.WORKFLOW_DATA_SQL_UPLOAD
    form_class = ScheduleSQLUploadForm

    # List of SQL connections that are enabled
    sql_connections = None

    # Connection used for this scheduled operation
    connection = None

    def _create_payload(
        self,
        request: http.HttpRequest,
        **kwargs
    ) -> dict:
        """Create a payload dictionary to store in the session.

        :param request: HTTP request
        :param kwargs: Dictionary with extra parameters
        :return: Dictionary with pairs name/value
        """
        payload = super()._create_payload(request, **kwargs)

        # Update payload
        payload.update({
            'workflow_id': self.workflow.id,
            'page_title': gettext('Schedule SQL Upload')})

        return payload

    def setup(self, request, *args, **kwargs):
        """Store available connections"""
        super().setup(request, *args, **kwargs)
        if not (connections := models.SQLConnection.objects.filter(
            enabled=True)
        ):
            raise OnTaskException(
                _('Incorrect scheduling of SQL Upload (zero connections)'))
        self.sql_connections = connections

        # If the invocation comes with one connection, use it.
        self.connection = kwargs.pop('connection', None)
        if (
            not self.connection
                and self.object
                and 'connection_id' in self.object.payload
        ):
            self.connection = self.sql_connections.get(
                pk=self.object.payload['connection_id'])

    def get_form_kwargs(self):
        """Fetch the available connections"""
        kwargs = super().get_form_kwargs()
        kwargs['sql_connections'] = self.sql_connections
        kwargs['connection'] = self.connection
        return kwargs

    def form_valid(self, form) -> http.HttpResponse:
        """Process the valid form."""
        # Save the connection ID
        self.op_payload['connection_id'] = form.cleaned_data['sql_connection']

        # Go straight to the final step
        return self.finish(self.request, self.op_payload)
