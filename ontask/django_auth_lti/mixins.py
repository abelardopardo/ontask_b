from builtins import object

from braces.views import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from ontask.django_auth_lti.verification import is_allowed


class LTIUtilityMixin(object):
    def get_lti_param(self, keyword, default=None):
        return self.request.LTI.get(keyword, default)

    def current_user_roles(self):
        return self.get_lti_param('roles', [])


class LTIRoleRestrictionMixin(LTIUtilityMixin):
    allowed_roles = None
    redirect_url = reverse_lazy('not_authorized')
    raise_exception = False

    def dispatch(self, request, *args, **kwargs):
        if self.allowed_roles is None:
            raise ImproperlyConfigured(
                _("'LTIRoleRestrictionMixin' requires "
                  "'allowed_roles' attribute to be set."))

        if is_allowed(request, self.allowed_roles, self.raise_exception):
            return super().dispatch(request, *args, **kwargs)

        return redirect(self.redirect_url)


class LTIRoleRequiredMixin(LoginRequiredMixin, LTIRoleRestrictionMixin):
    """Shortcut to use both LoginRequiredMixin and LTIRoleRestrictionMixin"""
