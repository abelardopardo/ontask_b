import datetime
from time import sleep
from zoneinfo import ZoneInfo

from celery.utils.log import get_task_logger
from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ontask import models
from ontask.core import is_instructor
from ontask.oauth import services

LOGGER = get_task_logger('celery_execution')


def canvas_do_burst_pause(burst: int, burst_pause: int, idx: int):
    """Detect end of burst and pause if needed.

    :param burst: Burst length
    :param burst_pause: Pause after length is reached
    :param idx: Current index
    :return:
    """
    if burst and (idx % burst) == 0:
        # Burst exists and the limit has been reached
        LOGGER.info(
            'Burst (%s) reached. Waiting for %s secs',
            str(burst),
            str(burst_pause))
        sleep(burst_pause)


@user_passes_test(is_instructor)
def canvas_get_or_set_oauth_token(
    request: HttpRequest,
    oauth_instance_name: str,
    continue_url: str,
    error_url: str
) -> http.HttpResponse:
    """Check for OAuth token, if not present, request a new one.

    Function that checks if the user has a Canvas OAuth token. If there is a
    token, the function goes straight to send the messages. If not, the OAuth
    process starts.

    :param request: Request object to process
    :param oauth_instance_name: Locator for the OAuth instance in OnTask
    :param continue_url: URL to continue if the token exists and is valid
    :param error_url: URL to redirect when an error is detected
    :return: Http response
    """
    # Get the information from the payload
    if not (oauth_info := settings.CANVAS_INFO_DICT.get(oauth_instance_name)):
        messages.error(
            request,
            _('Unable to obtain Canvas OAuth information'),
        )
        return redirect(error_url)

    # Check if we have the token
    if not (token := models.OAuthUserToken.objects.filter(
        user=request.user,
        instance_name=oauth_instance_name,
    ).first()):
        # There is no token, authentication has to take place for the first
        # time
        return services.get_initial_token_step1(
            request,
            oauth_info,
            reverse(continue_url))

    # Check if the token is valid
    now = datetime.datetime.now(ZoneInfo(settings.TIME_ZONE))
    if now > token.valid_until:
        try:
            services.refresh_token(token, oauth_info)
        except Exception as exc:
            # Something went wrong when refreshing the token
            messages.error(
                request,
                _('Error when invoking Canvas API: {0}.'.format(str(exc))),
            )
            return redirect(error_url)

    return redirect(continue_url)
