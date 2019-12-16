# -*- coding: utf-8 -*-

"""View to create a SQL upload/merge operation."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.utils.translation import ugettext as _

from ontask import models
from ontask.core import get_workflow, is_instructor
from ontask.dataops.services import sql_connection_select_table


@user_passes_test(is_instructor)
@get_workflow()
def sql_connection_index(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Show table of SQL connections for user to choose one.

    :param request: HTTP request
    :param workflow: Workflow of the current context.
    :return: HTTP response
    """
    del workflow
    table = sql_connection_select_table('scheduler:sqlupload')
    return render(
        request,
        'dataops/connections.html',
        {'table': table, 'is_sql': True, 'title': _('SQL Connections')})


@user_passes_test(is_instructor)
@get_workflow()
def schedule_sqlupload(
    request: http.HttpRequest,
    pk: int,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Schedule a SQL load/update operation

    :param request: Web request
    :param pk: primary key of the SQL conn used
    :param workflow: Workflow being used
    :return: Creates the upload_data dictionary in the session
    """
    conn = models.SQLConnection.objects.filter(
        pk=pk).filter(enabled=True).first()
    if not conn:
        return redirect('scheduelr:index')

    form = None
    if request.method == 'POST' and form.is_valid():
        pass

    return redirect('under_construction')
