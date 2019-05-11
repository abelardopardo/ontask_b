# -*- coding: utf-8 -*-

"""Functions to handle OAuth2 authentication."""

from datetime import timedelta

import requests
from django.conf import settings as ontask_settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework import status

from action.payloads import get_action_payload
from ontask.permissions import is_instructor
from ontask_oauth.models import OnTaskOAuthUserTokens

return_url_key = 'oauth_return_url'
oauth_hash_key = 'oauth_hash'
callback_url_key = 'callback_url'


def get_initial_token_step1(request, oauth_info, return_url):
    """Get initial token from the OAuth server.

    :param request: Received request

    :param oauth_info: a dict with the following fields:

    # {
    #   domain_port: VALUE,
    #   client_id: VALUE,
    #   client_secret: VALUE ,
    #   authorize_url: VALUE (format {0} for domain_port),
    #   access_token_url: VALUE (format {0} for domain_port),
    #   aux_params: DICT with additional parameters)
    # }

    :param return_url: URL to store as return URL after obtaining the token

    :return: Http response
    """
    # Remember the URL from which we are making the request so that we
    # can return once the Token has been obtained
    request.session[return_url_key] = return_url

    # Store in the session a random hash key to make sure the call back goes
    # back to the right request
    request.session[oauth_hash_key] = get_random_string()

    # Store the callback URL in the session
    request.session[callback_url_key] = request.build_absolute_uri(
        reverse('ontask_oauth:callback'),
    )

    # The parameters for the request are described in:
    # https://canvas.instructure.com/doc/api/file.oauth_endpoints.html
    domain = oauth_info['domain_port']
    return redirect(
        requests.Request(
            'GET',
            oauth_info['authorize_url'].format(domain),
            params={
                'client_id': oauth_info['client_id'],
                'response_type': 'code',
                'redirect_uri': request.session[callback_url_key],
                'scopes': 'url:POST|/api/v1/conversations',
                'state': request.session[oauth_hash_key],
            },
        ).prepare().url,
    )


def refresh_token(user_token, oauth_info):
    """Obtain OAuth2 token for the user in this request.

    :param user_token: User token to be refreshed
    :param oauth_info: a dict with the following fields:
    # {
    #   domain_port: VALUE,
    #   client_id: VALUE,
    #   client_secret: VALUE ,
    #   authorize_url: VALUE (format {0} for domain_port),
    #   access_token_url: VALUE (format {0} for domain_port),
    #   aux_params: DICT with additional parameters)
    # }
    :return: Updated token object (or exception if any anomaly is detected
    """
    # At this point we have the payload, the token and the OAuth configuration
    # information.
    domain = oauth_info['domain_port']
    response = requests.post(
        oauth_info['access_token_url'].format(domain),
        {
            'grant_type': 'refresh_token',
            'client_id': oauth_info['client_id'],
            'client_secret': oauth_info['client_secret'],
            'refresh_token': user_token.refresh_token,
            'redirect_uri': reverse('ontask_oauth:callback'),
        },
    )

    if response.status_code != status.HTTP_200_OK:
        raise Exception(_('Unable to refresh OAuth token.'))

    # Response is correct. Parse and extract elements
    response_data = response.json()

    # Get the new token and expire datetime and save the token
    user_token.access_token = response_data['access_token']
    user_token.valid_until = timezone.now() + timedelta(
        seconds=response_data.get('expires_in', 0))
    user_token.save()

    return user_token.access_token


@user_passes_test(is_instructor)
def callback(request):
    """Process the call received from the server.

    This is supposed to contain the token so it is saved to the database and
    then redirects to a page previously stored in the session object.

    :param request: Request object

    :return: Redirection to the stored page
    """
    # Get the payload from the session
    payload = get_action_payload(request)

    # If there is no payload, something went wrong.
    if payload is None:
        # Something is wrong with this execution. Return to action table.
        messages.error(
            request,
            _('Incorrect Canvas callback invocation.'))
        return redirect('action:index')

    # Check first if there has been some error
    error_string = request.GET.get('error')
    if error_string:
        messages.error(
            request,
            ugettext('Error in OAuth2 step 1 ({0})').format(error_string),
        )
        return redirect('action:index')

    # Verify if the state is the one expected (stored in the session)
    if request.GET.get('state') != request.session[oauth_hash_key]:
        # This call back does not match the appropriate request. Something
        # went wrong.
        messages.error(
            request,
            _('Inconsistent OAuth response. Unable to authorize'))
        return redirect('action:index')

    # Get the information from the payload
    oauth_instance = payload.get('target_url')
    if not oauth_instance:
        messages.error(
            request,
            _('Internal error. Empty OAuth Instance name'))
        return redirect('action:index')

    oauth_info = ontask_settings.CANVAS_INFO_DICT.get(oauth_instance)
    if not oauth_info:
        messages.error(
            request,
            _('Internal error. Invalid OAuth Dict element'))
        return redirect('action:index')

    # Correct response from a previous request. Obtain the access token,
    # the refresh token, and the expiration date.
    domain = oauth_info['domain_port']
    response = requests.post(
        oauth_info['access_token_url'].format(domain),
        {
            'grant_type': 'authorization_code',
            'client_id': oauth_info['client_id'],
            'client_secret': oauth_info['client_secret'],
            'redirect_uri': request.session[callback_url_key],
            'code': request.GET.get('code')})

    if response.status_code != status.HTTP_200_OK:
        # POST request was not successful
        messages.error(
            request, _('Unable to obtain access token from OAuth'))
        return redirect('action:index')

    # Response is correct. Parse and extract elements
    response_data = response.json()

    # Create the new token for the user
    utoken = OnTaskOAuthUserTokens(
        user=request.user,
        instance_name=oauth_instance,
        access_token=response_data['access_token'],
        refresh_token=response_data.get('refresh_token'),
        valid_until=timezone.now() + timedelta(
            seconds=response_data.get('expires_in', 0)),
    )
    utoken.save()

    return redirect(
        request.session.get(return_url_key, reverse('action:index')))
