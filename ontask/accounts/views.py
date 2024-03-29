"""Views created with code obtained from django-authtools."""

from typing import Dict

import six
from braces import views as bracesviews
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import RedirectURLMixin
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, resolve_url, reverse
from django.urls import reverse_lazy
from django.utils.functional import lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView

from ontask.accounts import forms

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

    class Mixin:
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


class WithCurrentSiteMixin:
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


class WithNextUrlMixin:
    redirect_field_name = REDIRECT_FIELD_NAME
    success_url = None

    def get_next_url(self):
        request = self.request
        if not (
            redirect_to := request.POST.get(
                self.redirect_field_name,
                request.GET.get(self.redirect_field_name, ''))
        ):
            return

        host = self.request.get_host()
        allowed_hosts = [host]

        try:
            allowed_hosts += self.get_success_url_allowed_hosts()
        except AttributeError:
            pass

        if url_has_allowed_host_and_scheme(
            redirect_to,
            allowed_hosts=allowed_hosts,
            require_https=self.request.is_secure()
        ):
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


class LoginView(
    bracesviews.AnonymousRequiredMixin,
    AuthDecoratorsMixin,
    RedirectURLMixin,
    WithCurrentSiteMixin,
    WithNextUrlMixin,
    FormView
):
    template_name = "accounts/login.html"
    form_class = forms.LoginForm
    authentication_form = None
    allow_authenticated = True
    next_page = resolve_url_lazy(settings.LOGIN_REDIRECT_URL)

    def dispatch(self, *args, **kwargs):
        if not self.allow_authenticated and self.request.user.is_authenticated:
            return redirect(reverse('home'))
        return super(LoginView, self).dispatch(*args, **kwargs)

    def get_form_class(self):
        return self.authentication_form or self.form_class

    def get_context_data(self, **kwargs) -> Dict:
        context = super(LoginView, self).get_context_data(**kwargs)
        context.update({
            self.redirect_field_name: self.request.GET.get(
                self.redirect_field_name, '',
            ),
        })
        context['ONTASK_SHOW_HOME_FOOTER_IMAGE'] = \
            settings.SHOW_HOME_FOOTER_IMAGE
        return context

    def form_valid(self, form):
        auth.login(self.request, form.get_user())
        redirect_response = super().form_valid(form)
        if (form.cleaned_data.get('remember_me')) is True:
            one_month = 30 * 24 * 60 * 60
            expiry = getattr(settings, 'KEEP_LOGGED_DURATION', one_month)
            self.request.session.set_expiry(expiry)
        return redirect_response


class PasswordChangeView(
    LoginRequiredMixin,
    WithNextUrlMixin,
    AuthDecoratorsMixin,
    FormView
):
    form_class = forms.PasswordChangeForm
    template_name = 'accounts/password-change.html'
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.get_user()
        return kwargs

    def get_user(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            _(
                'Your password was changed, '
                'hence you have been logged out. Please relogin'))
        # Updating the password logs out all other sessions for the user
        # except the current one if
        # django.contrib.auth.middleware.SessionAuthenticationMiddleware
        # is enabled.
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)


class LogoutView(RedirectView):
    http_method_names = ['get', 'post']

    def get_redirect_url(self, **kwargs):
        return reverse_lazy('home')

    def get(self, *args, **kwargs):
        auth.logout(self.request)
        return RedirectView.get(self, *args, **kwargs)
