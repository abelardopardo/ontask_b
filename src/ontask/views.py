# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

import logs.ops
from action import settings
from action.models import Action
from dataops import pandas_db, ops
from django_auth_lti.decorators import lti_role_required
from ontask.permissions import UserIsInstructor


class HomePage(generic.TemplateView):
    template_name = "home.html"


class AboutPage(generic.TemplateView):
    template_name = "about.html"


class ToBeDone(UserIsInstructor, generic.TemplateView):
    template_name = "base.html"


@login_required
def entry(request):
    return redirect('workflow:index')


@csrf_exempt
@xframe_options_exempt
@lti_role_required(['Instructor', 'Student'])
def lti_entry(request):
    return redirect('workflow:index')


# No permissions in this URL as it is supposed to be wide open to track email
#  reads.
def trck(request):
    """
    Receive a request with a token from email read tracking
    :param request: Request object
    :return: Reflects in the DB the reception and (optionally) in the data 
    table of the workflow
    """
    if request.method != 'GET':
        raise Http404

    # Detected attempt to track event
    track_id = request.GET.get('v', None)
    if not track_id:
        raise Http404

    # If the track_id is not correctly signed, out.
    try:
        track_id = signing.loads(track_id)
    except signing.BadSignature:
        raise Http404

    # The request is legit and the value has been verified. Track_id has now
    # the dictionary with the information included in the tracking

    # Get the objects related to the ping
    try:
        user = get_user_model().objects.get(email=track_id['sender'])
        action = Action.objects.get(pk=track_id['action'])
    except Exception:
        raise Http404

    # If the track comes with column_dst, the event needs to be reflected
    # back in the data frame
    column_dst = track_id.get('column_dst', '')

    if column_dst:
        # Load the dataframe
        data_frame = pandas_db.load_from_db(action.workflow.id)

        # Extract the relevant fields from the track_id
        column_to = track_id['column_to']
        msg_to = track_id['to']
        track_col_name = track_id['column_dst']
        # New val in DF: df.loc[df['a']==1,'b'] = VAL
        data_frame.loc[data_frame[column_to] == msg_to, track_col_name] += 1

        # Save DF
        ops.store_dataframe_in_db(data_frame, action.workflow.id)

        # Get the tracking column and update all the conditions in the
        # actions that have this column as part of their formulas
        track_col = action.workflow.columns.get(name=track_col_name)
        for action in action.workflow.actions.all():
            action.update_n_rows_selected(track_col)

    # Record the event
    logs.ops.put(
        user,
        'action_email_read',
        action.workflow,
        {'to': track_id['to'],  # The destination of the email
         'email_column': track_id['column_to'],  # The column used to get the
         'column_dst': column_dst
         }
    )

    return HttpResponse(settings.PIXEL, content_type='image/png')


@login_required
@csrf_exempt
def keep_alive(request):
    return JsonResponse({})


def ontask_handler400(request):
    response = render(request, '400.html', {})
    response.status_code = 400
    return response


def ontask_handler403(request):
    response = render(request, '403.html', {})
    response.status_code = 403
    return response


def ontask_handler404(request):
    response = render(request, '404.html', {})
    response.status_code = 404
    return response


def ontask_handler500(request):
    response = render(request, '500.html', {})
    response.status_code = 500
    return response
