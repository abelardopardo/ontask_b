# -*- coding: utf-8 -*-

"""Wrappers around asynchronous task executions."""

from django import http
from django.shortcuts import render


def ontask_handler400(
    request: http.HttpRequest,
    exception,
) -> http.HttpResponse:
    """Return error 400."""
    del exception
    response = render(request, '400.html', {})
    response.status_code = 400
    return response


def ontask_handler403(
    request: http.HttpRequest,
    exception,
) -> http.HttpResponse:
    """Return error 403."""
    del exception
    response = render(request, '403.html', {})
    response.status_code = 403
    return response


def ontask_handler404(
    request: http.HttpRequest,
    exception,
) -> http.HttpResponse:
    """Return error 404."""
    response = render(request, '404.html', {'exception': exception})
    response.status_code = 404
    return response


def ontask_handler500(request: http.HttpRequest) -> http.HttpResponse:
    """Return error 500."""
    response = render(request, '500.html', {})
    response.status_code = 500
    return response
