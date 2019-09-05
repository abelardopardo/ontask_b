
from builtins import object

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.contrib.auth import get_user_model

from ontask import models

User = get_user_model()


class UserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('name'),
        )

    class Meta(object):
        model = User
        fields = ['name']


class ProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('picture'),
            Field('bio'),
            Submit('update', 'Update', css_class="shadow btn-success"),
        )

    class Meta(object):
        model = models.Profile
        fields = ['picture', 'bio']
