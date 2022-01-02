# -*- coding: utf-8 -*-

"""Views to serve personalised messages."""
from typing import Optional

from django import http
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

from ontask import models
from ontask.action import forms, services
from ontask.core import ActionView, UserIsInstructor, has_access
from ontask.core.services import ontask_handler404


def _common_run_survey_row(
    request: http.HttpRequest,
    action: Optional[models.Action] = None,
    user_attribute_name: Optional[str] = None,
) -> http.HttpResponse:
    """Extract the survey row and create the Form to collect data."""
    # Access the data corresponding to the user
    is_manager = has_access(request.user, action.workflow)
    try:
        context = services.get_survey_context(
            request,
            is_manager,
            action,
            user_attribute_name)
    except services.OnTaskActionSurveyDataNotFound:
        return ontask_handler404(request, None)
    except services.OnTaskActionSurveyNoTableData as exc:
        exc.message_to_error(request)
        return redirect(reverse('action:run', kwargs={'pk': action.id}))

    # Get the active columns attached to the action
    colcon_items = services.extract_survey_questions(action, request.user)
    # Bind the form with the existing data
    form = forms.EnterActionIn(
        request.POST or None,
        tuples=colcon_items,
        context=context,
        values=[context[colcon.column.name] for colcon in colcon_items],
        show_key=is_manager)
    if (
        request.method == 'POST'
        and form.is_valid()
        and not request.POST.get('lti_version')
    ):
        services.update_row_values(
            request,
            action,
            form.get_key_value_pairs())
        # If not instructor, just thank the user!
        if not is_manager:
            return render(request, 'thanks.html', {})

        # Back to running the action
        return redirect(reverse('action:run', kwargs={'pk': action.id}))

    return render(
        request,
        'action/run_survey_row.html',
        {
            'form': form,
            'action': action,
            'cancel_url': reverse(
                'action:run', kwargs={'pk': action.id},
            ) if is_manager else None,
        },
    )


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(xframe_options_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ActionServeActionView(generic.View):
    """Serve the rendering of an action in a workflow for a given user.

    - uatn: User attribute name. The attribute to check for authentication.
      By default this will be "email".

    - uatv: User attribute value. The value to check with respect to the
      previous attribute. The default is the user attached to the request.

    If the two last parameters are given, the authentication is done as:

    user_record[user_attribute_name] == user_attribute_value.
    """

    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Get the action object
        action = models.Action.objects.filter(
            pk=kwargs.get('action_id')).prefetch_related(
            'conditions',
        ).first()
        if not action or (not action.serve_enabled) or (not action.is_active):
            raise http.Http404

        # Get the parameters
        user_attribute_name = request.GET.get('uatn', 'email')
        if user_attribute_name not in action.workflow.get_column_names():
            raise http.Http404

        if action.is_out:
            try:
                response = services.serve_action_out(
                    request.user,
                    action,
                    user_attribute_name)
            except Exception:
                raise http.Http404()

            return response

        return _common_run_survey_row(request, action, user_attribute_name)


class ActionServeActionLTIView(ActionServeActionView):
    """Serve an action accessed through LTI."""

    def get(self, request, *args, **kwargs):
        try:
            action_id = int(request.GET.get('id'))
        except Exception:
            raise http.Http404()

        return super().get(request, action_id=action_id)


class ActionRunSurveyRowView(UserIsInstructor, ActionView):
    """Render form for introducing information in a single row.

    Function that runs the action in for a single row. The request
    must have query parameters uatn = key name and uatv = key value to
    perform the lookup.
    """

    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.action.is_out:
            return redirect('action:index')

        return _common_run_survey_row(
            request,
            self.action,
            kwargs.get('uatn', 'email'))
