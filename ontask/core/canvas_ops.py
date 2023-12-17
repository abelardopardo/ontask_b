import datetime
import sys
from time import sleep
from typing import Tuple, Dict
from zoneinfo import ZoneInfo
import requests

from celery.utils.log import get_task_logger
from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from ontask import models
from ontask.core import is_instructor
from ontask.oauth import services
from ontask import OnTaskException

LOGGER = get_task_logger('celery_execution')

canvas_api_map = {}
if settings.CANVAS_INFO_DICT:
    canvas_api_map = {
        'get_course_quizzes': (requests.get, '{0}/api/v1/courses/{1}/quizzes'),
        'get_quiz_statistics': (
            requests.get,
            '{0}/api/v1/courses/{1}/quizzes/{2}/statistics'),
        'get_quiz_submissions': (
            requests.get,
            '{0}/api/v1/courses/{1}/quizzes/{2}/submissions'),
        'get_course_enrolment': (
            requests.get,
            '{0}/api/v1/courses/{1}/enrollments'
            '?type=StudentEnrollment&state={2}'),
        'get_course_assignments': (
            requests.get,
            '{0}/api/v1/courses/{1}/assignments'),
        'get_assignment_submissions': (
            requests.get,
            '{0}/api/v1/courses/{1}/assignments/{2}/submissions')
    }


def request_refresh_and_retry(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        request_method,
        url: str,
        headers: dict,
        **kwargs) -> HttpResponse:
    """Send a request and refresh token if needed.

    The method attempts a request with the given method, and if the response
    requires a token refresh, it refreshes the token and issues the request
    again.

    The method also checks if the Rate Limit Exceeded is returned, and if so,
    it delays the execution of the query.

    :param oauth_info: Object with the oauth information
    :param user_token: OAuth user token object
    :param request_method: function to use for the request (get, put, etc.)
    :param url: String with the URL to request
    :param headers: Dictionary with the headers to use in the request
    :param kwargs: Other arguments passed to the request
    """
    response = request_method(url, headers=headers, **kwargs)

    # Check if hte token needs refreshing
    if (
        response.status_code == status.HTTP_401_UNAUTHORIZED
        and response.headers.get('WWW-Authenticate')
    ):
        user_token = services.refresh_token(user_token, oauth_info)
        headers['Authorization'] = headers['Authorization'].format(
            user_token.access_token)
        response = request_method(url, headers, **kwargs)

    # Loop while the Rate Limit Exceeded is reached
    while (
                response.status_code == status.HTTP_403_FORBIDDEN and
                response.data == "403 Forbidden (Rate Limit Exceeded)"
    ):
        # Wait a minute
        sleep(60)
        response = request_method(url, headers, **kwargs)

    return response


def request_and_access(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        request_method,
        url: str,
        headers: dict,
        result_key: str = None,
        **kwargs):
    """Method to execute an API call and accumulate the
    result for multiple pages.

    :param oauth_info: Dictionary with the required oauth information
    :param user_token: Current token for authentication
    :param request_method: Request to execute
    :param url: URL to access
    :param headers: Dictionary with headers to use
    :param result_key: Dictionary key to accumulate the result. If this is none,
    then it is assumed to be a list.
    :param kwargs: Other additional parameters to include in the request.

    :return: JSON containing the result
    """
    if result_key:
        # Result is a dictionary with a single key pointing to a list
        result = {result_key: []}
    else:
        # Result is a list
        result = []

    # Execute multiple requests if there are pages of results
    while True:
        response = request_refresh_and_retry(
                oauth_info,
                user_token,
                request_method,
                url,
                headers,
                **kwargs)

        if result_key:
            result[result_key].extend(response.json()[result_key])
        else:
            new_data = response.json()
            if isinstance(new_data, list):
                result.extend(new_data)
            else:
                result.append(new_data)

        links = response.headers.get('link', None)
        if not links:
            # Whole information received
            break

        links = dict(
            [(c, b[1:-1]) for b, c in
             [a.split('; ') for a in links.split(',')]])

        # Check the links headers to see if there are additional pages
        if not (url := links.get('rel="next"', None)):
            # There is no link to access the next page. Terminate loop
            break

    # Return the accumulated result
    return result


def get_authorization_header(token: str) -> dict:
    """Returns header with the given token as Authorization element."""
    return {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Authorization': 'Bearer {0}'.format(token),
    }


@user_passes_test(is_instructor)
def get_or_set_oauth_token(
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


def get_oauth_and_user_token(
        user,
        target_url: str
) -> Tuple[Dict, models.OAuthUserToken]:
    """Retrieve oauth info and user token from the platform."""
    # Get the oauth info
    if (oauth_info := settings.CANVAS_INFO_DICT.get(target_url)) is None:
        raise Exception(_('Unable to find OAuth Information Record'))

    # Get the token
    if not (user_token := models.OAuthUserToken.objects.filter(
            user=user,
            instance_name=target_url,
    ).first()):
        # There is no token, execution cannot proceed
        raise Exception(_('Incorrect execution due to absence of token'))

    return oauth_info, user_token


def verify_course_id(
        course_id: int,
        log_item: models.Log = None) -> int:
    """Verifies that the given parameter is a positive integer."""
    if course_id is None:
        msg = _('Empty course_id detected.')
        if log_item:
            log_item.set_error_in_payload(msg)
        raise OnTaskException(msg)

    try:
        result = int(course_id)
        if result < 0:
            msg = _('Negative course id given.')
            if log_item:
                log_item.set_error_in_payload(msg)
            raise OnTaskException(msg)
    except ValueError:
        msg = _('Incorrect course id given.')
        if log_item:
            log_item.set_error_in_payload(msg)
        raise OnTaskException(msg)

    return result


def get_course_enrolment(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        course_id: int,
        student_state: str = 'active'
) -> dict:
    """Get list of active students enrolled in a course."""
    # Get request method and URL for the endpoint from the map in this module
    request_method, endpoint = canvas_api_map['get_course_enrolment']

    return request_and_access(
        oauth_info,
        user_token,
        request_method,
        endpoint.format(oauth_info['domain_port'], course_id, student_state),
        get_authorization_header(user_token.access_token))


def get_course_quizzes(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        course_id: int) -> list:
    """Gets all the quizzes within a course"""
    # Get request method and URL for the endpoint from the map in this module
    request_method, endpoint = canvas_api_map['get_course_quizzes']

    return request_and_access(
        oauth_info,
        user_token,
        request_method,
        endpoint.format(oauth_info['domain_port'], course_id),
        get_authorization_header(user_token.access_token))


def get_course_assignments(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        course_id: int) -> list:
    """Gets all the assignments within a course"""
    # Get request method and URL for the endpoint from the map in this module
    request_method, endpoint = canvas_api_map['get_course_assignments']

    return request_and_access(
        oauth_info,
        user_token,
        request_method,
        endpoint.format(oauth_info['domain_port'], course_id),
        get_authorization_header(user_token.access_token))


def get_quiz_statistics(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        course_id: int,
        quiz_id: int
) -> dict:
    """Get all statistics for a quiz in a course."""
    request_method, endpoint = canvas_api_map['get_quiz_statistics']

    return request_and_access(
        oauth_info,
        user_token,
        request_method,
        endpoint.format(oauth_info['domain_port'], course_id, quiz_id),
        get_authorization_header(user_token.access_token),
        result_key='quiz_statistics')


def get_quiz_submissions(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        course_id: int,
        quiz_id: int
) -> dict:
    """Get all submissions for a quiz in a course."""
    request_method, endpoint = canvas_api_map['get_quiz_submissions']

    return request_and_access(
        oauth_info,
        user_token,
        requests.get,
        endpoint.format(oauth_info['domain_port'], course_id, quiz_id),
        get_authorization_header(user_token.access_token),
        result_key='quiz_submissions')


def get_assignment_submissions(
        oauth_info: dict,
        user_token: models.OAuthUserToken,
        course_id: int,
        assignment_id: int
) -> dict:
    """Get all assignment submissions in a course"""
    request_method, endpoint = canvas_api_map['get_assignment_submissions']

    return request_and_access(
        oauth_info,
        user_token,
        requests.get,
        endpoint.format(oauth_info['domain_port'], course_id, assignment_id),
        get_authorization_header(user_token.access_token))
