# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, reverse, render
from django.template.loader import render_to_string
from django.utils.html import format_html
import django_tables2 as tables
from django_tables2 import RequestConfig, A

from ontask import is_instructor, decorators
from workflow.models import Workflow
from .models import Log
from .ops import log_types
from . import settings


class LogTable(tables.Table):

    # Needs to be in the table to be used as URL parameter
    id = tables.Column(visible=False)

    created = tables.DateTimeColumn(
        attrs={'th': {'style': 'text-align:center;'},
               'td': {'style': 'text-align:center;'}},
        verbose_name='Date/Time')
    user = tables.EmailColumn(
        attrs={'th': {'style': 'text-align:center;'},
               'td': {'style': 'text-align:center;'}},
        accessor=A('user.email')
    )
    name = tables.Column(
        attrs={'th': {'style': 'text-align:center;'},
               'td': {'style': 'text-align:center;'}},
        verbose_name=str('Event type')
    )
    payload = tables.Column(
        attrs={'th': {'style': 'text-align:center;'},
               'td': {'style': 'text-align:center;'}},
        orderable=False,
        verbose_name=str('Additional data')
    )

    def render_payload(self, record):
        return format_html(
            """
            <button type="submit" class="btn btn-primary btn-sm js-log-view"
                    data-url="{0}">
              <span class="glyphicon glyphicon-eye-open"> View</span>
            </button>
            """.format(reverse('logs:view', kwargs={'pk': record.id}))
        )

    class Meta:
        model = Log
        sequence = ('created', 'user', 'name', 'payload')
        exclude = ('id', 'workflow')

        attrs = {
            'class': 'table table-stripped table-bordered table-hover',
            'id': 'log-table'
        }


@login_required
@user_passes_test(is_instructor)
def show(request):

    workflow = get_object_or_404(Workflow,
                                 pk=request.session.get('ontask_workflow_id',
                                                        -1),
                                 user=request.user)
    # Initial value for the context
    context = {'workflow': workflow}

    # Get the relevant logs (user and workflow)
    logs = Log.objects.filter(
        user=request.user,
        workflow__id=request.session.get('ontask_workflow_id', -1)
    )

    # If the number of logs is zero, bypass table rendering.
    if len(logs) == 0:
        # No logs found for this workflow
        context['msg'] = 'No data available for this workflow'
        return render(request, 'logs/show.html', context)

    # Create the table and populate the request
    table = LogTable(logs)

    RequestConfig(
        request,
        paginate={'per_page': int(str(getattr(settings,
                                              'PAGE_SIZE')))}).configure(table)
    context['table'] = table

    # Render the page with the table
    return render(request, 'logs/show.html', context)


@login_required
@user_passes_test(is_instructor)
def view(request, pk):

    # Get the log item
    log_item = Log.objects.get(pk=pk)
    data = dict()

    context = json.loads(log_item.payload)

    # Add the name of the object and the type
    context['log_type'] = log_item.name
    context['op_name'] = log_types[log_item.name]

    # Render the template and return as JSON response
    data['html_form'] = render_to_string(
        'logs/includes/partial_log_view.html',
        context,
        request=request)

    return JsonResponse(data)
