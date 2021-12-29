# -*- coding: utf-8 -*-


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.contrib.auth import (
    forms as authforms, get_user_model, password_validation)
from django.contrib.auth.forms import (
    AuthenticationForm,
    ReadOnlyPasswordHashField, ReadOnlyPasswordHashWidget,
    UserChangeForm as DjangoUserChangeForm)
from django.contrib.auth.hashers import (
    UNUSABLE_PASSWORD_PREFIX, identify_hasher)
from django.forms.utils import flatatt
from django.utils.html import format_html
from django.utils.translation import ugettext, ugettext_lazy as _

User = get_user_model()


def _is_password_usable(pw):
    """Decide if a password is usable only by the unusable password prefix.

    We can't use django.contrib.auth.hashers.is_password_usable either,
    because it not only checks against the unusable password, but checks for
    a valid hash function too. We need different error messages in those cases.
    """

    return not pw.startswith(UNUSABLE_PASSWORD_PREFIX)


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['username'].widget.input_type = 'email'  # ugly hack
        self.fields['username'].label = _('Email address')

        self.helper.layout = Layout(
            Field('username', placeholder=_('Enter Email'), autofocus=''),
            Field('password', placeholder=_('Enter Password')),
            Submit(
                'sign_in', _('Log in'),
                css_class='btn btn-lg btn-block spin'),
            # HTML('<a href="{}">Forgot Password?</a>'.format(
            #    reverse('accounts:password-reset'))),
            Field('remember_me'),
        )


class PasswordChangeForm(authforms.PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field(
                'old_password',
                placeholder='Enter old password',
                autofocus=''),
            Field('new_password1', placeholder='Enter new password'),
            Field('new_password2', placeholder='Enter new password (again)'),
            Submit(
                'pass_change',
                'Change Password',
                css_class='btn-outline-primary'),
        )


class SetPasswordForm(authforms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            Field(
                'new_password1',
                placeholder='Enter new password',
                autofocus=''),
            Field('new_password2', placeholder='Enter new password (again)'),
            Submit(
                'pass_change',
                'Change Password',
                css_class='btn-outline-primary'))


class BetterReadOnlyPasswordHashWidget(ReadOnlyPasswordHashWidget):
    """
    A ReadOnlyPasswordHashWidget that has a less intimidating output.
    """

    def render(self, name, value, attrs=None, renderer=None):
        final_attrs = flatatt(self.build_attrs(attrs))

        if not value or not _is_password_usable(value):
            summary = ugettext("No password set.")
        else:
            try:
                identify_hasher(value)
            except ValueError:
                summary = ugettext("Invalid password format or unknown"
                                   " hashing algorithm.")
            else:
                summary = ugettext('*************')

        return format_html(
            '<div{attrs}><strong>{summary}</strong></div>',
            attrs=final_attrs,
            summary=summary)


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'duplicate_username':
            _("A user with that %(username)s already exists.")}

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput)

    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above,"
                    " for verification."))

    class Meta:
        model = User
        fields = (User.USERNAME_FIELD,) + tuple(User.REQUIRED_FIELDS)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        def validate_uniqueness_of_username_field(value):
            # Since User.username is unique, this check is redundant,
            # but it sets a nicer error message than the ORM. See #13147.
            try:
                User._default_manager.get_by_natural_key(value)
            except User.DoesNotExist:
                return value
            raise forms.ValidationError(
                self.error_messages['duplicate_username'] % {
                    'username': User.USERNAME_FIELD})

        self.fields[User.USERNAME_FIELD].validators.append(
            validate_uniqueness_of_username_field)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def _post_clean(self):
        super(UserCreationForm, self)._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('password2', error)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on the user,
    but replaces the password field with admin password hash display field.
    """
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        widget=BetterReadOnlyPasswordHashWidget)

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class AdminUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(AdminUserChangeForm, self).__init__(*args, **kwargs)
        if not self.fields['password'].help_text:
            self.fields['password'].help_text = \
                DjangoUserChangeForm.base_fields['password'].help_text
