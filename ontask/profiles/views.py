

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from rest_framework.authtoken.models import Token

from ontask import models
from ontask.core.permissions import is_instructor
from ontask.profiles import forms


class ShowProfile(LoginRequiredMixin, generic.TemplateView):
    template_name = "profiles/show_profile.html"
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        if slug:
            profile = get_object_or_404(models.Profile, slug=slug)
            user = profile.user
        else:
            user = self.request.user

        if user == self.request.user:
            kwargs["editable"] = True
        kwargs["show_user"] = user
        kwargs["tokens"] = models.OAuthUserToken.objects.filter(
            user=user
        )
        return super().get(request, *args, **kwargs)


class EditProfile(LoginRequiredMixin, generic.TemplateView):
    template_name = "profiles/edit_profile.html"
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if "user_form" not in kwargs:
            kwargs["user_form"] = forms.UserForm(instance=user)
        if "profile_form" not in kwargs:
            kwargs["profile_form"] = forms.ProfileForm(instance=user.profile)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        del args, kwargs
        user = self.request.user
        user_form = forms.UserForm(request.POST, instance=user)
        profile_form = forms.ProfileForm(request.POST,
                                         request.FILES,
                                         instance=user.profile)
        if not (user_form.is_valid() and profile_form.is_valid()):
            messages.error(request,
                           _("There was a problem with the form. "
                             "Please check the details."))
            user_form = forms.UserForm(instance=user)
            profile_form = forms.ProfileForm(instance=user.profile)
            return super().get(request,
                               user_form=user_form,
                               profile_form=profile_form)
        # Both forms are fine. Time to save!
        user_form.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.save()
        messages.success(request, _("Profile details saved!"))
        return redirect("profiles:show_self")


@login_required
def reset_token(request):
    """
    Function to reset the authentication token for a user. If it exists,
    it is deleted first.
    :param request:
    :return:
    """
    tk = Token.objects.filter(user=request.user).first()

    if tk:
        # Delete it if detected.
        tk.delete()

    # Create the new one
    Token.objects.create(user=request.user)

    # Go back to showing the profile
    return redirect('profiles:show_self')


@user_passes_test(is_instructor)
def delete_token(request, pk):
    """
    Function to delete the authentication token for a server.
    :param request: Request received
    :param pk: Token id to remove
    :return:
    """
    del request
    models.OAuthUserToken.objects.get(id=pk).delete()
    return redirect('profiles:show_self')
