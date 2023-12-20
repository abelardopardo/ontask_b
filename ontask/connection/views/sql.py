"""Views to handle SQL connections."""

from django.urls import reverse
from django.views import generic

from ontask import models
from ontask.connection import forms, services
from ontask.connection.views import common


class SQLConnectionAdminIndexView(common.ConnectionAdminIndexView):
    """Show and handle the SQL connections."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'table': services.create_sql_connection_admintable(),
            'data_url': reverse('connection:sqlconn_create')})
        return context


class SQLConnectionIndexView(common.ConnectionIndexView):
    """Show the SQL connections."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = services.create_sql_connection_runtable(
            'dataops:sqlupload_start')
        return context


class SQLConnectionCreateView(
    common.ConnectionBaseCreateEditView,
    generic.CreateView
):
    """Create a new SQL view."""

    model = models.SQLConnection
    form_class = forms.SQLConnectionForm
    event_type = models.SQLConnection.create_event
    add = True

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.action_url = reverse('connection:sqlconn_create')


class SQLConnectionEditView(
    common.ConnectionBaseCreateEditView,
    generic.UpdateView,
):
    """Edit an existing view."""

    model = models.SQLConnection
    form_class = forms.SQLConnectionForm
    event_type = models.SQLConnection.edit_event
    add = False

    """Edit an SQL connection object."""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.action_url = reverse(
            'connection:sqlconn_edit',
            kwargs={'pk': kwargs['pk']})
