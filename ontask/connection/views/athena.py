"""Views to handle Athena connections."""

from django.urls import reverse
from django.views import generic

from ontask import models
from ontask.connection import forms, services
from ontask.connection.views import common


class AthenaConnectionAdminIndexView(common.ConnectionAdminIndexView):
    """Show and handle the Athena connections."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'table': services.create_athena_connection_admintable(),
            'data_url': reverse('connection:athenaconn_create')})
        return context


class AthenaConnectionIndexView(common.ConnectionIndexView):
    """Show the Athena connections."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = services.create_athena_connection_runtable()
        return context


class AthenaConnectionShowView(common.ConnectionShowView):
    """Show the Athena connection in a modal."""

    model = models.SQLConnection


class AthenaConnectionCreateView(
    common.ConnectionBaseCreateEditView,
    generic.CreateView):
    """Create a new Athena view."""

    model = models.AthenaConnection
    form_class = forms.AthenaConnectionForm
    event_type = models.AthenaConnection.create_event
    add = True

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.action_url = reverse('connection:athenaconn_create')


class AthenaConnectionEditView(
    common.ConnectionBaseCreateEditView,
    generic.UpdateView
):
    """Edit an existing athena connection view."""

    model = models.AthenaConnection
    form_class = forms.AthenaConnectionForm
    event_type = models.AthenaConnection.edit_event
    add = False

    """Edit an Athena connection object."""

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.action_url = reverse(
            'connection:athenaconn_edit',
            kwargs={'pk': kwargs['pk']})


class AthenaConnectionDeleteView(common.ConnectionDeleteView):
    """Delete an Athena connection."""

    model = models.AthenaConnection


class AthenaConnectionCloneView(common.ConnectionCloneView):
    """Process the Clone Athena Connection view."""

    model = models.AthenaConnection
    mgr = models.AthenaConnection.objects


class AthenaConnectionToggleView(common.ConnectionToggleView):
    """Process the Athena Toggle Connection view."""

    model = models.AthenaConnection
