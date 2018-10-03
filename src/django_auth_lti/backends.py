import logging
from time import time

import oauth2
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from ontask_lti.tool_provider import DjangoToolProvider
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


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

        logger.info(_("about to begin authentication process"))

        if not request:
            logger.error(
                _("No request object in authenticaiton")
            )
            return None

        request_key = request.POST.get('oauth_consumer_key', None)

        if request_key is None:
            logger.error(
                _("Request doesn't contain an oauth_consumer_key; can't "
                  "continue."))
            return None

        if not settings.LTI_OAUTH_CREDENTIALS:
            logger.error(_("Missing LTI_OAUTH_CREDENTIALS in settings"))
            raise PermissionDenied

        secret = settings.LTI_OAUTH_CREDENTIALS.get(request_key)

        if secret is None:
            logger.error(
                _("Could not get a secret for key {0}").format(request_key)
            )
            raise PermissionDenied

        logger.debug(_('using key/secret {0}/{1}').format(request_key, secret))
        tool_provider = DjangoToolProvider(request_key, secret,
                                           request.POST.dict())

        postparams = request.POST.dict()

        logger.debug(_('request is secure: {0}').format(request.is_secure()))
        for key in postparams:
            logger.debug(_('POST {0}: {1}').format(key, postparams.get(key)))

        logger.debug(
            _('request abs url is {0}').format(request.build_absolute_uri())
        )

        for key in request.META:
            logger.debug(
                _('META {0}: {1}').format(key, request.META.get(key))
            )

        logger.info(_("about to check the signature"))

        try:
            request_is_valid = tool_provider.is_valid_request(request)
        except oauth2.Error:
            logger.exception(
                _('error attempting to validate LTI launch {0}').format(
                    postparams
                )
            )
            request_is_valid = False

        if not request_is_valid:
            logger.error(_("Invalid request: signature check failed."))
            raise PermissionDenied

        logger.info(_("done checking the signature"))

        logger.info(
            _("about to check the timestamp: {0}").format(int(
                tool_provider.oauth_timestamp
            ))
        )

        if time() - int(tool_provider.oauth_timestamp) > 60 * 60:
            logger.error(_("OAuth timestamp is too old."))
            # raise PermissionDenied
        else:
            logger.info(_("timestamp looks good"))

        logger.info(_("done checking the timestamp"))

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

        # Check that we have an email field at least
        if not email:
            logger.error(_("Invalid request: Invalid email."))
            raise PermissionDenied

        logger.info(_("We have a valid username: {0}").format(username))

        UserModel = get_user_model()

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if self.create_unknown_user:
            user, created = UserModel.objects.get_or_create(**{
                # UserModel.USERNAME_FIELD: username,
                'email': email,
            })

            if created:
                logger.debug(
                    _('authenticate created a new user for {0}').format(
                        username
                    )
                )
            else:
                logger.debug(
                    _('authenticate found an existing user for '
                      '{0}').format(username)
                )

        else:
            logger.debug(
                _('automatic new user creation is turned OFF! just try to '
                  'find and existing record'))
            try:
                user = UserModel.objects.get_by_natural_key(username)
            except UserModel.DoesNotExist:
                logger.debug(
                    _('authenticate could not find user {0}').format(username)
                )
                # should return some kind of error here?
                pass

        # update the user
        if email:
            user.email = email
        if username:
            user.name = username
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.save()
        logger.debug(_("updated the user record in the database"))

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
