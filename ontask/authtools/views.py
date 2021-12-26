# -*- coding: utf-8 -*-
"""

Mostly equivalent to the views from django.contrib.auth.views,
but implemented as class-based views.

"""
import warnings

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import SuccessURLAllowedHostsMixin
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, resolve_url
from django.urls import reverse_lazy
from django.utils.functional import lazy
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView, TemplateView
import six

from .forms import AuthenticationForm

User = get_user_model()


def _safe_resolve_url(url):
    """
    Previously, resolve_url_lazy would fail if the url was a unicode object.
    See <https://github.com/fusionbox/django-authtools/issues/13> for more
    information.

    Thanks to GitHub user alanwj for pointing out the problem and providing
    this solution.
    """
    return six.text_type(resolve_url(url))


resolve_url_lazy = lazy(_safe_resolve_url, six.text_type)


class WithCurrentSiteMixin(object):
    def get_current_site(self):
        return get_current_site(self.request)

    def get_context_data(self, **kwargs):
        kwargs = super(WithCurrentSiteMixin, self).get_context_data(**kwargs)
        current_site = self.get_current_site()
        kwargs.update({
            'site': current_site,
            'site_name': current_site.name,
        })
        return kwargs


class WithNextUrlMixin(object):
    redirect_field_name = REDIRECT_FIELD_NAME
    success_url = None

    def get_next_url(self):
        request = self.request
        redirect_to = request.POST.get(
            self.redirect_field_name,
            request.GET.get(self.redirect_field_name, ''))
        if not redirect_to:
            return

        host = self.request.get_host()
        allowed_hosts = [host]

        try:
            allowed_hosts += self.get_success_url_allowed_hosts()
        except AttributeError:
            pass

        url_is_safe = is_safe_url(
            redirect_to,
            allowed_hosts=allowed_hosts,
            require_https=self.request.is_secure()
        )

        if url_is_safe:
            return redirect_to

    # This mixin can be mixed with FormViews and RedirectViews. They each use
    # a different method to get the URL to redirect to, so we need to provide
    # both methods.
    def get_success_url(self):
        return self.get_next_url() or super(
            WithNextUrlMixin,
            self).get_success_url()

    def get_redirect_url(self, **kwargs):
        return self.get_next_url() or super(
            WithNextUrlMixin,
            self).get_redirect_url(**kwargs)


def decorator_mixin(decorator):
    """
    Converts view function decorator into a mixin for a class-based view.

    ::

        LoginRequiredMixin = DecoratorMixin(login_required)

        class MyView(LoginRequiredMixin):
            pass

        class SomeView(DecoratorMixin(some_decorator),
                       DecoratorMixin(something_else)):
            pass

    """

    class Mixin(object):
        __doc__ = decorator.__doc__

        @classmethod
        def as_view(cls, *args, **kwargs):
            view = super(Mixin, cls).as_view(*args, **kwargs)
            return decorator(view)

    Mixin.__name__ = str('DecoratorMixin(%s)' % decorator.__name__)
    return Mixin


NeverCacheMixin = decorator_mixin(never_cache)
CsrfProtectMixin = decorator_mixin(csrf_protect)
LoginRequiredMixin = decorator_mixin(login_required)
SensitivePostParametersMixin = decorator_mixin(
    sensitive_post_parameters(
        'password',
        'old_password',
        'password1',
        'password2',
        'new_password1',
        'new_password2'))


class AuthDecoratorsMixin(
    NeverCacheMixin,
    CsrfProtectMixin,
    SensitivePostParametersMixin,
):
    pass


class LoginView(
    AuthDecoratorsMixin,
    SuccessURLAllowedHostsMixin,
    WithCurrentSiteMixin,
    WithNextUrlMixin,
    FormView
):
    form_class = AuthenticationForm
    authentication_form = None
    template_name = 'registration/login.html'
    allow_authenticated = True
    success_url = resolve_url_lazy(settings.LOGIN_REDIRECT_URL)

    # BBB: This is deprecated (See LoginView.get_allow_authenticated)
    disallow_authenticated = None

    def get_allow_authenticated(self):
        if self.disallow_authenticated is not None:
            warnings.warn(
                "disallow_authenticated is deprecated. Please use "
                "allow_authenticated",
                DeprecationWarning)
            return not self.disallow_authenticated
        else:
            return self.allow_authenticated

    def dispatch(self, *args, **kwargs):
        allow_authenticated = self.get_allow_authenticated()
        if not allow_authenticated and self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super(LoginView, self).dispatch(*args, **kwargs)

    def get_form_class(self):
        return self.authentication_form or self.form_class

    def form_valid(self, form):
        auth.login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs = super(LoginView, self).get_context_data(**kwargs)
        kwargs.update({
            self.redirect_field_name: self.request.GET.get(
                self.redirect_field_name, '',
            ),
        })
        return kwargs


class LogoutView(
    NeverCacheMixin,
    SuccessURLAllowedHostsMixin,
    WithCurrentSiteMixin,
    WithNextUrlMixin,
    TemplateView,
    RedirectView
):
    template_name = 'registration/logged_out.html'
    permanent = False

    def get_redirect_url(self, **kwargs):
        redirect_to = super(LogoutView, self).get_redirect_url(**kwargs)

        if redirect_to:
            return redirect_to
        elif settings.LOGOUT_REDIRECT_URL is not None:
            return resolve_url(settings.LOGOUT_REDIRECT_URL)
        elif self.request.POST.get(
            self.redirect_field_name, self.request.GET.get(
                self.redirect_field_name, '')):
            # we have a url, but it is not safe. Django redirects back to the
            # same view.
            return self.request.path

    def get(self, *args, **kwargs):
        auth.logout(self.request)
        # If we have a url to redirect to, do it. Otherwise render the
        # logged-out template.
        if self.get_redirect_url(**kwargs):
            return RedirectView.get(self, *args, **kwargs)
        else:
            return TemplateView.get(self, *args, **kwargs)


class PasswordChangeView(
    LoginRequiredMixin,
    WithNextUrlMixin,
    AuthDecoratorsMixin,
    FormView
):
    template_name = 'registration/password_change_form.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')

    def get_form_kwargs(self):
        kwargs = super(PasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self.get_user()
        return kwargs

    def get_user(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one if
        # django.contrib.auth.middleware.SessionAuthenticationMiddleware
        # is enabled.
        update_session_auth_hash(self.request, form.user)
        return super(PasswordChangeView, self).form_valid(form)


class PasswordChangeDoneView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/password_change_done.html'
