

from authtools import views as authviews
from braces import views as bracesviews
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from . import forms

User = get_user_model()


class LoginView(bracesviews.AnonymousRequiredMixin,
                authviews.LoginView):
    template_name = "accounts/login.html"
    form_class = forms.LoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ONTASK_SHOW_HOME_FOOTER_IMAGE'] = \
            settings.SHOW_HOME_FOOTER_IMAGE
        return context

    def form_valid(self, form):
        redirect = super().form_valid(form)
        remember_me = form.cleaned_data.get('remember_me')
        if remember_me is True:
            one_month = 30 * 24 * 60 * 60
            expiry = getattr(settings, "KEEP_LOGGED_DURATION", one_month)
            self.request.session.set_expiry(expiry)
        return redirect


class LogoutView(authviews.LogoutView):
    url = reverse_lazy('home')


class PasswordChangeView(authviews.PasswordChangeView):
    form_class = forms.PasswordChangeForm
    template_name = 'accounts/password-change.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        messages.success(self.request,
                         _("Your password was changed, "
                           "hence you have been logged out. Please relogin"))
        return super().form_valid(form)


class PasswordResetView(authviews.PasswordResetView):
    form_class = forms.PasswordResetForm
    template_name = 'accounts/password-reset.html'
    success_url = reverse_lazy('accounts:password-reset-done')
    subject_template_name = 'accounts/emails/password-reset-subject.txt'
    email_template_name = 'accounts/emails/password-reset-email.html'


class PasswordResetDoneView(authviews.PasswordResetDoneView):
    template_name = 'accounts/password-reset-done.html'


class PasswordResetConfirmView(authviews.PasswordResetConfirmAndLoginView):
    template_name = 'accounts/password-reset-confirm.html'
    form_class = forms.SetPasswordForm
