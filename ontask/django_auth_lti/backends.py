import logging
from time import time

import oauth2
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group

from ontask.lti.tool_provider import DjangoToolProvider

logger = logging.getLogger('ontask')


class LTIAuthBackend(ModelBackend):
    """
    By default, the ``authenticate`` method creates ``User`` objects for
    usernames that don't already exist in the database.  Subclasses can disable
    this behavior by setting the ``create_unknown_user`` attribute to
    ``False``.
    """

    # Create a User object if not already in the database?
    create_unknown_user = True
    # Username prefix for users without an sis source id
    unknown_user_prefix = "cuid:"

    def authenticate(self, request, username=None, password=None, **kwargs):

        if settings.DEBUG:
            logger.info("about to begin authentication process")

        if not request:
            logger.error("No request object in authentication")
            return None

        request_key = request.POST.get('oauth_consumer_key')

        if request_key is None:
            logger.error(
                "Request doesn't contain an oauth_consumer_key; can't "
                + "continue.")
            return None

        if not settings.LTI_OAUTH_CREDENTIALS:
            logger.error("Missing LTI_OAUTH_CREDENTIALS in settings")
            raise PermissionDenied

        secret = settings.LTI_OAUTH_CREDENTIALS.get(request_key)

        if secret is None:
            logger.error(
                "Could not get a secret for key %s", request_key
            )
            raise PermissionDenied

        logger.debug('using key/secret %s/%s', request_key, secret)
        tool_provider = DjangoToolProvider(request_key, secret,
            request.POST.dict())

        postparams = request.POST.dict()

        logger.debug('request is secure: %s', request.is_secure())
        for key in postparams:
            logger.debug('POST %s: %s', key, postparams.get(key))

        logger.debug('request abs url is %s', request.build_absolute_uri())

        for key in request.META:
            logger.debug('META %s: %s', key, request.META.get(key))

        logger.info("about to check the signature")

        try:
            request_is_valid = tool_provider.is_valid_request(request)
        except oauth2.Error:
            logger.exception('error attempting to validate LTI launch %s',
                postparams)
            request_is_valid = False

        if not request_is_valid:
            logger.error("Invalid request: signature check failed.")
            raise PermissionDenied

        logger.info("done checking the signature")
        logger.info(
            "about to check the timestamp: {%s",
            int(tool_provider.oauth_timestamp))

        if time() - int(tool_provider.oauth_timestamp) > 60 * 60:
            logger.error("OAuth timestamp is too old.")
            # raise PermissionDenied
        else:
            logger.info("timestamp looks good")

        logger.info("done checking the timestamp")

        # (this is where we should check the nonce)

        # if we got this far, the user is good

        user = None

        # Retrieve username from LTI parameter or default to an overridable
        # function return value
        username = tool_provider.lis_person_sourcedid or \
                   self.get_default_username(
                       tool_provider,
                       prefix=self.unknown_user_prefix
                   )
        username = self.clean_username(username)  # Clean it

        email = tool_provider.lis_person_contact_email_primary
        first_name = tool_provider.lis_person_name_given
        last_name = tool_provider.lis_person_name_family
        roles = tool_provider.roles

        # Check that we have an email field at least
        if not email:
            logger.error("Invalid request: Invalid email.")
            raise PermissionDenied

        logger.info("We have a valid username: %s", username)

        user_model = get_user_model()

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if self.create_unknown_user:
            user, created = user_model.objects.get_or_create(**{
                # user_model.USERNAME_FIELD: username,
                'email': email,
            })

            if created:
                logger.debug(
                    'authenticate created a new user for %s', username)
            else:
                logger.debug('authenticate found an existing user for %s',
                    username)

        else:
            logger.debug(
                'automatic new user creation is turned OFF! just try to '
                'find and existing record'
            )
            try:
                user = user_model.objects.get_by_natural_key(username)
            except user_model.DoesNotExist:
                logger.debug('authenticate could not find user %s', username)

        # update user information if given by LTI and not present in user obj.
        if not user.name and username:
            user.name = username
        if not user.name and first_name and last_name:
            user.name = first_name + ' ' + last_name

        # check if substring group_role in the user's launch roles
        should_be_in_instructor_group = any(
            any(group_role_substring in role for role in roles) \
            for group_role_substring in settings.LTI_INSTRUCTOR_GROUP_ROLES
        )
        if should_be_in_instructor_group and not user.groups.filter(name='instructor').exists():
            instructor_group = Group.objects.get(name='instructor')
            user.groups.add(instructor_group)

        user.save()
        logger.debug("updated the user record in the database")

        return user

    def clean_username(self, username):
        return username

    def get_default_username(self, tool_provider, prefix=''):
        """
        Return a default username value from tool_provider in case offical
        LTI param lis_person_sourcedid was not present.
        """
        # Default back to user_id lti param
        uname = tool_provider.get_custom_param(
            'canvas_user_id') or tool_provider.user_id
        return prefix + uname
