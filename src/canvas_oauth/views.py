# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from datetime import timedelta

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import reverse, redirect
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _, ugettext
from rest_framework import status

from ontask.permissions import is_instructor
from .models import CanvasUserTokens

return_url_key = 'oauth_return_url'
oauth_hash_key = 'oauth_hash'
callback_url_key = 'callback_url'


def get_initial_token_step1(request):
    """
     Obtain a OAuth2 token from Canvas for the user in this request
    :param request: Received request
    :return:
    """
    # Remember the URL from which we are making the request so that we
    # can return once the Token has been obtained
    request.session[return_url_key] = request.get_full_path()

    # Store in the session a random hash key to make sure the call back goes
    # back to the right request
    request.session[oauth_hash_key] = get_random_string()

    # Store the callback URL in the session
    request.session[callback_url_key] = request.build_absolute_uri(
        reverse('canvas_oauth:callback')
    )

    # Redirect the call to the CANVAS_AUTHORIZE_URL

    # The parameters for the request are described in:
    # https://canvas.instructure.com/doc/api/file.oauth_endpoints.html
    return redirect(
        requests.Request('GET',
                         settings.CANVAS_AUTHORIZE_URL,
                         params={
                             'client_id': settings.CANVAS_CLIENT_ID,
                             'response_type': 'code',
                             'redirect_uri': request.session[callback_url_key],
                             'state': request.session[callback_url_key],
                         }).prepare().url
    )


@user_passes_test(is_instructor)
def callback(request):
    """
    Callback received from Canvas. This is supposed to contain the token
    so it is saved to the database and then redirects to a page previously
    stored in the session object.
    :param request: Request object
    :return: Redirection to the stored page
    """

    # Obtain the URL to redirect as response to this request
    return_url = request.session.get('return_url_key',
                                     reverse('workflow:index'))

    # Check first if there has been some error
    error_string = request.GET.get('error', None)
    if error_string:
        messages.error(
            request,
            ugettext('Error in OAuth2 step 1 ({0})').format(error_string)
        )
        return redirect(return_url)

    # Verify if the state is the one expected (stored in the session)
    if request.session[oauth_hash_key] != request.GET.get('state'):
        # This call back does not match the appropriate request. Something
        # went wrong.
        messages.error(request,
                       _('Inconsistent OAuth response. Unable to authorize'))
        return redirect(return_url)

    # Correct response from a previous request. Obtain the access token,
    # the refresh token, and the expiration date.
    response = requests.post(settings.CANVAS_ACCESS_TOKEN,
                             {'grant_type': 'authorization_code',
                              'client_id': settings.CANVAS_CLIENT_ID,
                              'client_secret': settings.CANVAS_CLIENT_SECRET,
                              'redirect_uri': request[callback_url_key],
                              'code': request.GET.get('code')})

    if response.status != status.HTTP_200_OK:
        # POST request was not successful
        messages.error(request,
                       _('Unable to obtain access token from Canvas'))
        return redirect(return_url)

    # Response is correct. Parse and extract elements
    response_data = response.json()

    # Create the new token for the user
    utoken = CanvasUserTokens(
        user=request.user,
        access_token=response_data['access_token'],
        refresh_token=response_data.get('refresh_token', None),
        valid_until=timezone.now() + \
                    timedelta(seconds=response_data['expires_in'])
    )
    utoken.save()

    return redirect(return_url)
