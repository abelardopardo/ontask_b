# -*- coding: utf-8 -*-

"""Classes and functions to manage Amazon Athena connections."""

import django_tables2 as tables
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from ontask import create_new_name
from ontask.core.decorators import ajax_required
from ontask.core.permissions import is_admin, is_instructor
from ontask.core.tables import OperationsColumn
from ontask.dataops.forms import AthenaConnectionForm
from ontask.models import Log, AthenaConnection
from ontask.workflow.access import remove_workflow_from_session


class AthenaConnectionTableAdmin(tables.Table):
    """Table to render the Athena admin items."""

    operations = OperationsColumn(
        verbose_name='',
        template_file='dataops/includes/partial_athenaconn_adminop.html',
        template_context=lambda record: {'id': record['id']},
    )

    def render_name(self, record):
        """Render name as a link."""
        return format_html(
            '<a class="js-athenaconn-edit" href="#" data-url="{0}">{1}</a>',
            reverse('dataops:athenaconn_edit', kwargs={'pk': record['id']}),
            record['name'],
        )

    class Meta:
        """Define model, fields, sequence and attributes."""

        model = AthenaConnection

        fields = ('name', 'description_text')

        sequence = ('name', 'description_text', 'operations')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'athenaconn-admin-table',
        }


class AthenaConnectionTableRun(tables.Table):
    """Class to render the table of Athena connections."""

    operations = OperationsColumn(
        verbose_name='',
        template_file='dataops/includes/partial_athenaconn_runop.html',
        template_context=lambda record: {'id': record['id']},
    )

    def render_name(self, record):
        """Render the name as a link."""
        return format_html(
            '<a class="js-athenaconn-view" href="#" data-url="{0}">{1}</a>',
            reverse('dataops:athenaconn_view', kwargs={'pk': record['id']}),
            record['name'],
        )

    class Meta:
        """Define models, fields, sequence and attributes."""

        model = AthenaConnection

        fields = ('name', 'description_text')

        sequence = ('name', 'description_text', 'operations')

        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'athenaconn-instructor-table',
        }


def _save_conn_form(
    request: HttpRequest,
    form: AthenaConnectionForm,
    template_name: str,
) -> JsonResponse:
    """Save the connection provided in the form.

    :param request: HTTP request

    :param form: form object with the collected information

    :param template_name: To render the response

    :return: AJAX response
    """
    # Type of event to record
    is_add = form.instance.id is None

    # If it is a POST and it is correct
    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        conn = form.save()

        if form.instance.id:
            event_type = Log.ATHENA_CONNECTION_EDIT
        else:
            event_type = Log.ATHENA_CONNECTION_CREATE
        conn.log(request.user, event_type)

        return JsonResponse({'html_redirect': ''})

    # Request is a GET
    return JsonResponse({
        'html_form': render_to_string(
            template_name,
            {'form': form, 'id': form.instance.id, 'add': is_add},
            request=request)})



@user_passes_test(is_admin)
def athenaconnection_admin_index(request: HttpRequest) -> HttpResponse:
    """Show and handle the Athena connections.

    :param request: Request

    :return: Render the appropriate page.
    """
    remove_workflow_from_session(request)

    return render(
        request,
        'dataops/athena_connections_admin.html',
        {
            'table': AthenaConnectionTableAdmin(
                AthenaConnection.objects.values(
                    'id',
                    'name',
                    'description_text'),
                orderable=False)})


@user_passes_test(is_instructor)
def athenaconnection_instructor_index(request: HttpRequest) -> HttpResponse:
    """Render a page showing a table with the Athena connections.

    :param request:

    :return:
    """
    return render(
        request,
        'dataops/athena_connections.html',
        {
            'table': AthenaConnectionTableRun(
                AthenaConnection.objects.values(
                    'id',
                    'name',
                    'description_text'),
                orderable=False)})


@user_passes_test(is_instructor)
@ajax_required
def athenaconn_view(request: HttpRequest, pk: int) -> JsonResponse:
    """Show the Athena connection in a modal.

    :param request: Request object

    :param pk: Primary key of the Athena connection

    :return: AJAX response
    """
    # Get the connection object
    c_obj = AthenaConnection.objects.filter(pk=pk)
    if not c_obj:
        # Connection object not found, go to table of Athena connections
        return JsonResponse(
            {'html_redirect': reverse('dataops:athenaconns_admin_index')})

    return JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_show_athena_connection.html',
            {
                'c_vals': c_obj.values()[0],
                'id': c_obj[0].id,
                'request': request,
            },
        ),
    })


@user_passes_test(is_admin)
@ajax_required
def athenaconn_add(request: HttpRequest) -> JsonResponse:
    """Create a new Athena connection processing the GET/POST requests.

    :param request: Request object

    :return: AJAX response
    """
    # Create the form
    form = AthenaConnectionForm(request.POST or None)

    return _save_conn_form(
        request,
        form,
        'dataops/includes/partial_athenaconn_addedit.html')


@user_passes_test(is_admin)
@ajax_required
def athenaconn_edit(request: HttpRequest, pk: int) -> JsonResponse:
    """Respond to the reqeust to edit a Athena CONN object.

    :param request: HTML request

    :param pk: Primary key

    :return:
    """
    # Get the connection
    conn = AthenaConnection.objects.filter(pk=pk).first()
    if not conn:
        return JsonResponse({'html_redirect': reverse('home')})

    # Create the form
    form = AthenaConnectionForm(request.POST or None, instance=conn)

    return _save_conn_form(
        request,
        form,
        'dataops/includes/partial_athenaconn_addedit.html')


@user_passes_test(is_admin)
@ajax_required
def athenaconn_clone(request: HttpRequest, pk: int) -> JsonResponse:
    """AJAX handshake to clone an Athena connection.

    :param request: HTTP request

    :param pk: ID of the connection to clone.

    :return: AJAX response
    """
    context = {'pk': pk}  # For rendering

    # Get the connection
    conn = AthenaConnection.objects.filter(pk=pk).first()
    if not conn:
        # The view is not there. Redirect to workflow detail
        return JsonResponse({'html_redirect': reverse('home')})

    # Get the name of the connection to clone
    context['cname'] = conn.name

    if request.method == 'GET':
        return JsonResponse({
            'html_form': render_to_string(
                'dataops/includes/partial_athenaconn_clone.html',
                context,
                request=request),
        })

    # POST REQUEST

    # Proceed to clone the connection
    conn.id = None
    conn.name = create_new_name(conn.name, AthenaConnection.objects)
    conn.save()

    # Log the event
    conn.log(request.user, Log.ATHENA_CONNECTION_CLONE)

    return JsonResponse({'html_redirect': ''})


@user_passes_test(is_admin)
@ajax_required
def athenaconn_delete(request: HttpRequest, pk: int) -> JsonResponse:
    """AJAX processor for the delete athena connection operation.

    :param request: AJAX request

    :param pk: primary key for the athena connection

    :return: AJAX response to handle the form
    """
    # Get the connection
    conn = AthenaConnection.objects.filter(pk=pk).first()
    if not conn:
        return JsonResponse({'html_redirect': reverse('home')})

    if request.method == 'POST':
        conn.log(request.user, Log.ATHENA_CONNECTION_DELETE)
        conn.delete()
        return JsonResponse({'html_redirect': reverse('home')})

    # This is a GET request
    return JsonResponse({
        'html_form': render_to_string(
            'dataops/includes/partial_athenaconn_delete.html',
            {'athenaconn': conn},
            request=request),
    })
