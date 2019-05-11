
import json
import logging
from builtins import object
from collections import OrderedDict

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from .timer import Timer

logger = logging.getLogger('onTask')


class LTIAuthMiddleware(object):
    """
    Middleware for authenticating users via an LTI launch URL.

    If the request is an LTI launch request, then this middleware attempts to
    authenticate the username and signature passed in the POST data.
    If authentication is successful, the user is automatically logged in to
    persist the user in the session.

    If the request is not an LTI launch request, do nothing.
    """

    def process_request(self, request):
        logger.debug('inside process_request %s' % request.path)
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            logger.debug(_('improperly configured: requeset has no user attr'))
            raise ImproperlyConfigured(
                _("The Django LTI auth middleware requires the"
                  " authentication middleware to be installed.  Edit your"
                  " MIDDLEWARE_CLASSES setting to insert"
                  " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                  " before the PINAuthMiddleware class."))

        if request.method == 'POST' and request.POST.get('lti_message_type') == 'basic-lti-launch-request':

            logger.debug(_('received a basic-lti-launch-request - '
                           'authenticating the user'))

            # authenticate and log the user in
            with Timer() as t:
                user = auth.authenticate(request=request)
            logger.debug(_('authenticate() took %s s') % t.secs)

            if user is not None:
                # User is valid.  Set request.user and persist user in the session
                # by logging the user in.

                logger.debug(
                    _('user was successfully authenticated; now log them in')
                )
                request.user = user
                with Timer() as t:
                    auth.login(request, user)

                logger.debug('login() took %s s' % t.secs)

                lti_launch = {
                    'context_id': request.POST.get('context_id'),
                    'context_label': request.POST.get('context_label'),
                    'context_title': request.POST.get('context_title'),
                    'context_type': request.POST.get('context_type'),
                    'custom_canvas_account_id': request.POST.get('custom_canvas_account_id'),
                    'custom_canvas_account_sis_id': request.POST.get('custom_canvas_account_sis_id'),
                    'custom_canvas_api_domain': request.POST.get('custom_canvas_api_domain'),
                    'custom_canvas_course_id': request.POST.get('custom_canvas_course_id'),
                    'custom_canvas_membership_roles': request.POST.get('custom_canvas_membership_roles', '').split(','),
                    'custom_canvas_enrollment_state': request.POST.get('custom_canvas_enrollment_state'),
                    'custom_canvas_user_id': request.POST.get('custom_canvas_user_id'),
                    'custom_canvas_user_login_id': request.POST.get('custom_canvas_user_login_id'),
                    'launch_presentation_css_url': request.POST.get('launch_presentation_css_url'),
                    'launch_presentation_document_target': request.POST.get('launch_presentation_document_target'),
                    'launch_presentation_height': request.POST.get('launch_presentation_height'),
                    'launch_presentation_locale': request.POST.get('launch_presentation_locale'),
                    'launch_presentation_return_url': request.POST.get('launch_presentation_return_url'),
                    'launch_presentation_width': request.POST.get('launch_presentation_width'),
                    'lis_course_offering_sourcedid': request.POST.get('lis_course_offering_sourcedid'),
                    'lis_outcome_service_url': request.POST.get('lis_outcome_service_url'),
                    'lis_person_contact_email_primary': request.POST.get('lis_person_contact_email_primary'),
                    'lis_person_name_family': request.POST.get('lis_person_name_family'),
                    'lis_person_name_full': request.POST.get('lis_person_name_full'),
                    'lis_person_name_given': request.POST.get('lis_person_name_given'),
                    'lis_person_sourcedid': request.POST.get('lis_person_sourcedid'),
                    'lti_message_type': request.POST.get('lti_message_type'),
                    'resource_link_description': request.POST.get('resource_link_description'),
                    'resource_link_id': request.POST.get('resource_link_id'),
                    'resource_link_title': request.POST.get('resource_link_title'),
                    'roles': request.POST.get('roles', '').split(','),
                    'selection_directive': request.POST.get('selection_directive'),
                    'tool_consumer_info_product_family_code': request.POST.get('tool_consumer_info_product_family_code'),
                    'tool_consumer_info_version': request.POST.get('tool_consumer_info_version'),
                    'tool_consumer_instance_contact_email': request.POST.get('tool_consumer_instance_contact_email'),
                    'tool_consumer_instance_description': request.POST.get('tool_consumer_instance_description'),
                    'tool_consumer_instance_guid': request.POST.get('tool_consumer_instance_guid'),
                    'tool_consumer_instance_name': request.POST.get('tool_consumer_instance_name'),
                    'tool_consumer_instance_url': request.POST.get('tool_consumer_instance_url'),
                    'user_id': request.POST.get('user_id'),
                    'user_image': request.POST.get('user_image'),
                }
                # If a custom role key is defined in project, merge into existing role list
                if hasattr(settings, 'LTI_CUSTOM_ROLE_KEY'):
                    custom_roles = request.POST.get(settings.LTI_CUSTOM_ROLE_KEY, '').split(',')
                    lti_launch['roles'] += [_f for _f in custom_roles if _f]  # Filter out any empty roles

                request.session['LTI_LAUNCH'] = lti_launch

            else:
                # User could not be authenticated!
                logger.warning(
                    _('user could not be authenticated via LTI params; let '
                      'the request continue in case another auth plugin is '
                      'configured')
                )

        # Other functions in django-auth-lti expect there to be an LTI attribute on the request object
        # This enables backwards compatibility with consumers of this package who still want to use this
        # single launch version of LTIAuthMiddleware
        setattr(request, 'LTI', request.session.get('LTI_LAUNCH', {}))
        if not request.LTI:
            logger.warning(_("Could not find LTI launch parameters"))

    def clean_username(self, username, request):
        """
        Allows the backend to clean the username, if the backend defines a
        clean_username method.
        """
        backend_str = request.session[auth.BACKEND_SESSION_KEY]
        backend = auth.load_backend(backend_str)
        try:
            logger.debug(
                _('calling the backend {0} clean_username with {1}').format(
                backend, username
                )
            )
            username = backend.clean_username(username)
            logger.debug(_('cleaned username is {0}').format(username))
        except AttributeError:  # Backend has no clean_username method.
            pass
        return username
