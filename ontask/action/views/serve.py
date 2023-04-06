"""Views to serve personalised messages.

URLs used as entry points:

  - serve/?pk=nn (may come from outside the platform through LTI)

  - <pk>/run_survey_row/ (must come from inside the platform)

- ServeActionView
  - Action Out: GET
    - Get action and attribute
    - Render Template (services.serve_action_out)
  ELSE:
    # Action In
    - GET
      - Get action and attribute
      - is_manager
      - Create context
      - colcon_items
      - Create form
      - render action/run
    - POST
      - Get action and attribute
      - is_manager
      - Create context
      - colcon_items
      - create form
      - UPDATE ROW VALUES!

ServeActionLTI
  - id = request.GET.get('id')
  - call super (ServerActionView)

RunSurveyRowView -- Action In
  - If action is out -> ERROR
  - Use Serve action View
"""

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from ontask import models
from ontask.action import forms, services
from ontask.core import ActionView, UserIsInstructor, has_access, is_instructor


class ActionServeActionBasicView(generic.FormView):
    """Process request for action serve."""

    http_method_names = ['get', 'post']
    form_class = forms.EnterActionIn
    template_name = 'action/run_survey_row.html'
    action = None
    user_attribute_name = None

    def dispatch(self, request, *args, **kwargs):
        """Check action is obtained, correct and attributes in place."""
        # Check that action has been obtained
        if self.action is None:
            messages.error(request, _('Action not found'))
            return redirect('action:index')

        # Intercept when using an incorrect action.
        if (
            not is_instructor(self.request.user) and (
                not self.action or
                not self.action.serve_enabled or
                not self.action.is_active)
        ):
            messages.error(request, _('Action is not enabled.'))
            return redirect('action:index')

        # Get the parameters
        user_attribute_name = request.GET.get('uatn', 'email')
        if user_attribute_name not in self.action.workflow.get_column_names():
            messages.error(request, _('Unable to identify the user.'))
            return redirect('action:index')

        self.user_attribute_name = user_attribute_name

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        is_manager = has_access(self.request.user, self.action.workflow)
        try:
            context = services.get_survey_context(
                self.request,
                is_manager,
                self.action,
                self.user_attribute_name)
        except (
            services.OnTaskActionSurveyDataNotFound,
            services.OnTaskActionSurveyNoTableData
        ) as exc:
            raise http.Http404(str(exc))

        # Get the active columns attached to the action
        colcon_items = services.extract_survey_questions(
            self.action,
            self.request.user)

        kwargs.update({
            'tuples': colcon_items,
            'context': context,
            'values': [
                context[colcon.column.name] for colcon in colcon_items],
            'show_key': is_manager
        })

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'action': self.action,
            'cancel_url': reverse(
                'action:run',
                kwargs={'pk': self.action.id}) if has_access(
                self.request.user,
                self.action.workflow) else None})
        return context

    def get(self, request, *args, **kwargs) -> http.HttpResponse:
        if self.action.is_out:
            try:
                return services.serve_action_out(
                    request.user,
                    self.action,
                    self.user_attribute_name)
            except Exception:
                messages.error(request, _('Unable to process the action.'))
                return redirect('action:index')

        # Only for action-in requests, process form and page as normal.
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs) -> http.HttpResponse:
        if self.action.is_out:
            # Request is incorrect for thsi type of action
            raise http.Http404()

        if request.POST.get('lti_version'):
            # if the request has lti_version: process as a GET!
            return self.get(request, *args, **kwargs)

        # Post received followed a previous get. Keep processing
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # Update the newly received values in the table
        services.update_row_values(
            self.request,
            self.action,
            form.get_key_value_pairs())

        # If not instructor, just thank the user!
        if not has_access(self.request.user, self.action.workflow):
            return render(self.request, 'thanks.html', {})

        # Back to running the action
        return redirect(reverse('action:run', kwargs={'pk': self.action.id}))


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(xframe_options_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ActionServeActionLTIView(ActionServeActionBasicView):
    """Serve an action accessed through LTI."""

    action = None
    workflow = None

    def dispatch(self, request, *args, **kwargs):
        """Get the action in the object with the request parameter"""
        try:
            action_id = int(request.GET.get('pk'))
        except Exception:
            messages.error(request, _('Action not found'))
            return redirect('action:index')

        self.action = models.Action.objects.filter(pk=action_id).first()
        if not self.action:
            messages.error(request, _('Action not found'))
            return redirect('home')

        return super().dispatch(request, *args, **kwargs)


class ActionRunSurveyRowView(
    UserIsInstructor,
    ActionView,
    ActionServeActionBasicView,
):
    """Render form for introducing information in a single row.

    Runs the action in for a single row. The request must have query
    parameter uatn = key name to perform the user lookup.
    """

    def dispatch(self, request, *args, **kwargs):
        """Get the action in the object with the given view parameter"""
        if self.workflow is None:
            return redirect(reverse('home'))
        self.action = self.get_object()
        return super().dispatch(request, *args, **kwargs)
