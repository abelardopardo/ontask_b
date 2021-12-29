# -*- coding: utf-8 -*-

"""Classes and functions to show connections to regular users."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.utils.translation import gettext as _

from ontask import models
from ontask.connection import services
from ontask.core import get_workflow, is_instructor


@user_passes_test(is_instructor)
@get_workflow()
def sql_connection_index(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow] = None,
) -> http.HttpResponse:
    """Render a page showing a table with the available SQL connections.

    :param request: HTML request
    :param workflow: Current workflow being used
    :return: HTML response
    """
    del workflow
    table = services.sql_connection_select_table('dataops:sqlupload_start')
    return render(
        request,
        'connection/index.html',
        {'table': table, 'is_sql': True, 'title': _('SQL Connections')})


@user_passes_test(is_instructor)
@get_workflow()
def athena_connection_instructor_index(
    request: http.HttpRequest,
    workflow: Optional[models.Workflow],
) -> http.HttpResponse:
    """Render a page showing a table with the available Athena connections.

    :param request: HTML request
    :param workflow: Current workflow being used
    :return: HTML response
    """
    del workflow
    return render(
        request,
        'connection/index.html',
        {
            'table': services.create_athena_connection_runtable(),
            'is_athena': True,
            'title': _('Athena Connections')})
