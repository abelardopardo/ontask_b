"""Functions to handle OAuth2 authentication."""
from datetime import timedelta
from typing import Dict, Optional

import requests
from django import http
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from ontask import models
from ontask.core import session_ops

return_url_key = 'oauth_return_url'
oauth_hash_key = 'oauth_hash'
callback_url_key = 'callback_url'


def get_initial_token_step1(
    request: http.HttpRequest,
    oauth_info: Dict,
    return_url: str,
) -> http.HttpResponse:
    """Get initial token from the OAuth server.

    :param request: Received request
    :param oauth_info: a dict with the following fields:
        # {
        #   domain_port: VALUE (format example https://host:port),
        #   client_id: VALUE,
        #   client_secret: VALUE ,
        #   authorize_url: VALUE (format {0} for domain_port),
        #   access_token_url: VALUE (format {0} for domain_port),
        #   aux_params: DICT with additional parameters
        # }
    :param return_url: URL to store as return URL after obtaining the token
    :return: Http response
    """
    # Remember the URL from which we are making the request so that we
    # can return once the Token has been obtained
    request.session[return_url_key] = return_url

    # Store in the session a random hash key to make sure the call back goes
    # to the right request
    request.session[oauth_hash_key] = get_random_string(20)

    # Store the callback URL in the session
    request.session[callback_url_key] = request.build_absolute_uri(
        reverse('oauth:callback'),
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
                'state': request.session[oauth_hash_key],
            },
        ).prepare().url,
    )


def refresh_token(
        user_token: models.OAuthUserToken,
        oauth_info
) -> models.OAuthUserToken:
    """Obtain OAuth2 token for the user in this request.

    :param user_token: User token to be refreshed
    :param oauth_info: a dict with the following fields:
    # {
    #   domain_port: VALUE (format example https://host:port,
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
            'refresh_token': user_token.refresh_token,
            'redirect_uri': reverse('oauth:callback')},
        verify=True,
        allow_redirects=False,
        auth=(oauth_info['client_id'], oauth_info['client_secret']))

    if response.status_code != status.HTTP_200_OK:
        raise Exception(_('Unable to refresh OAuth token.'))

    # Response is correct. Parse and extract elements
    response_data = response.json()

    # Get the new token and expire datetime and save the token
    user_token.access_token = response_data['access_token']
    user_token.valid_until = timezone.now() + timedelta(
        seconds=response_data.get('expires_in', 0))

    user_token.save()

    return user_token


def process_callback(request: http.HttpRequest) -> Optional[str]:
    """Extract the token and store for future calls.

    :param request: Http Request received
    :return: Error message or None if everything has gone correctly.
    """
    # Correct response from a previous request. Obtain the access token,
    # the refresh token, and the expiration date.
    # Verify if the state is the one expected (stored in the session)
    if request.GET.get('state') != request.session[oauth_hash_key]:
        # This call back does not match the appropriate request. Something
        # went wrong.
        return _('Inconsistent OAuth response. Unable to authorize')

    if not (payload := session_ops.get_payload(request)):
        return _('Internal error. Empty payload in callback')

    if not (oauth_instance := payload.get('target_url')):
        return _('Internal error. Empty OAuth Instance name')

    oauth_info = settings.CANVAS_INFO_DICT.get(oauth_instance)
    if not oauth_info:
        return _('Internal error. Invalid OAuth Dict element')

    domain = oauth_info['domain_port']
    response = requests.post(
        oauth_info['access_token_url'].format(domain),
        {
            'grant_type': 'authorization_code',
            'redirect_uri': request.session[callback_url_key],
            'code': request.GET.get('code')},
        verify=True,
        allow_redirects=False,
        auth=(oauth_info['client_id'], oauth_info['client_secret']))

    if response.status_code != status.HTTP_200_OK:
        return _('Unable to obtain access token from OAuth')

    # Response is correct. Parse and extract elements
    response_data = response.json()

    # Create the new token for the user
    utoken = models.OAuthUserToken(
        user=request.user,
        instance_name=oauth_instance,
        access_token=response_data['access_token'],
        refresh_token=response_data.get('refresh_token'),
        valid_until=timezone.now() + timedelta(
            seconds=response_data.get('expires_in', 0)),
    )
    utoken.save()

    return None
