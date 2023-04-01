"""Backend class to authenticate LTI requests."""
from time import time
from typing import Mapping, Optional

from django import http
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
import oauth2

from ontask import LOGGER
from ontask.lti.tool_provider import DjangoToolProvider


class LTIAuthBackend(ModelBackend):
    """Class to authenticate a LTI  request.

    By default, the ``authenticate`` method creates ``User`` objects for
    usernames that don't already exist in the database.  Subclasses can disable
    this behavior by setting the ``create_unknown_user`` attribute to
    ``False``.
    """
    # Create a User object if not already in the database?
    create_unknown_user = True
    # Username prefix for users without an sis source id
    unknown_user_prefix = 'cuid:'

    def authenticate(
        self,
        request: http.HttpRequest,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs: Mapping,
    ):
        """Try to authenticate an LTI request."""
        if settings.DEBUG:
            LOGGER.info('Begin authentication process')

        if not request:
            if settings.DEBUG:
                LOGGER.info('No request object in authentication')
            return None

        request_key = request.POST.get('oauth_consumer_key')

        if request_key is None:
            LOGGER.debug(
                'Request does not contain an oauth_consumer_key. Stopping')
            return None

        if not settings.LTI_OAUTH_CREDENTIALS:
            LOGGER.debug('Missing LTI_OAUTH_CREDENTIALS in settings')
            raise PermissionDenied

        secret = settings.LTI_OAUTH_CREDENTIALS.get(request_key)

        if secret is None:
            LOGGER.debug('Could not get a secret for key %s', request_key)
            raise PermissionDenied

        LOGGER.debug('using key/secret %s/%s', request_key, secret)
        tool_provider = DjangoToolProvider(
            request_key,
            secret,
            request.POST.dict())

        postparams = request.POST.dict()

        LOGGER.debug('Request is secure: %s', request.is_secure())
        if settings.DEBUG:
            for key in postparams:
                LOGGER.debug('POST %s: %s', key, postparams.get(key))
            LOGGER.debug('Request abs url is %s', request.build_absolute_uri())

            for key in request.META:
                LOGGER.debug('META %s: %s', key, request.META.get(key))

        LOGGER.info('Checking the signature')

        try:
            request_is_valid = tool_provider.is_valid_request(request)
        except oauth2.Error:
            LOGGER.exception(
                'error attempting to validate LTI launch %s',
                postparams)
            request_is_valid = False

        if not request_is_valid:
            LOGGER.error('Invalid request: signature check failed.')
            raise PermissionDenied

        LOGGER.info('done checking the signature')
        LOGGER.info(
            'about to check the timestamp: {%s}',
            int(tool_provider.oauth_timestamp))

        if time() - int(tool_provider.oauth_timestamp) > 60 * 60:
            LOGGER.error('OAuth timestamp is too old.')
            # raise PermissionDenied
        else:
            LOGGER.info('Valid timestamp')

        LOGGER.info('Done checking the timestamp')

        # (this is where we should check the nonce)

        # if we got this far, the user is good

        user = None

        # Retrieve username from LTI parameter or default to an overridable
        # function return value
        username = (
            tool_provider.lis_person_sourcedid or
            self.get_default_username(
                tool_provider,
                prefix=self.unknown_user_prefix))

        email = tool_provider.lis_person_contact_email_primary
        first_name = tool_provider.lis_person_name_given
        last_name = tool_provider.lis_person_name_family
        roles = tool_provider.roles

        # Check that we have an email field at least
        if not email:
            LOGGER.error('Invalid request: Invalid email.')
            raise PermissionDenied

        LOGGER.info('Valid username: %s', username)

        user_model = get_user_model()

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if self.create_unknown_user:
            user, created = user_model.objects.get_or_create(email=email)

            if created:
                LOGGER.debug(
                    'Authenticate created a new user for %s',
                    username)
            else:
                LOGGER.debug(
                    'Authenticate found an existing user for %s',
                    username)

        else:
            LOGGER.debug(
                'automatic user creation disbled. Find and existing record')
            try:
                user = user_model.objects.get_by_natural_key(username)
            except user_model.DoesNotExist:
                LOGGER.debug('authenticate could not find user %s', username)

        # update user information if given by LTI and not present in user obj.
        if not user.name and username:
            user.name = username
        if not user.name and first_name and last_name:
            user.name = first_name + ' ' + last_name

        # check if substring group_role in the user's launch roles
        should_be_in_instructor_group = any(
            group_role_substring in roles
            for group_role_substring in settings.LTI_INSTRUCTOR_GROUP_ROLES
        )
        if (
            should_be_in_instructor_group
            and not user.groups.filter(name='instructor').exists()
        ):
            user.groups.add(Group.objects.get(name='instructor'))

        user.save()
        LOGGER.debug('Updated the user record in the database')

        return user

    @staticmethod
    def get_default_username(tool_provider, prefix=''):
        """Return a default username value from tool_provider.

        This is needed in case offical LTI param lis_person_sourcedid is not
        present.
        """
        # Default back to user_id lti param
        uname = tool_provider.get_custom_param(
            'canvas_user_id') or tool_provider.user_id
        return prefix + uname
