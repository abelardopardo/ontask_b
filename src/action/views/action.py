# -*- coding: utf-8 -*-

"""Views to render the list of actions."""

from builtins import object
from typing import Optional, Union

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views import generic

from action.forms import ActionForm, ActionUpdateForm
from action.models import Action
from action.payloads import action_session_dictionary
from action.views.edit_personalized import edit_action_out
from action.views.edit_survey import edit_action_in
from logs.models import Log
from ontask import simplify_datetime_str
from ontask.permissions import UserIsInstructor, is_instructor
from ontask.tables import OperationsColumn
from ontask.decorators import get_workflow, check_workflow
from workflow.models import Workflow


class ActionTable(tables.Table):
    """Class to render the list of actions per workflow.

    The Operations column is taken from another class to centralise the
    customisation.
    """

    name = tables.Column(verbose_name=_('Name'))

    description_text = tables.Column(verbose_name=_('Description'))

    action_type = tables.Column(verbose_name=_('Type'))

    last_executed_log = tables.Column(
        verbose_name=_('Last executed'),
        empty_values=['', None],
    )

    #
    # Operatiosn available per action type (see partial_action_operations.html)
    #
    #  Action type               |  Email  |  ZIP |  URL  |  RUN  |
    #  ------------------------------------------------------------
    #  Personalized text         |    X    |   X  |   X   |   X   |
    #  Personalized canvas email |    X    |      |       |   X   |
    #  Personalized JSON         |         |      |   ?   |   X   |
    #  Survey                    |         |      |   X   |   X   |
    #  Todo List                 |         |      |   X   |   X   |
    #
    operations = OperationsColumn(
        verbose_name='',
        template_file='action/includes/partial_action_operations.html',
        template_context=lambda record: {
            'id': record.id,
            'action_tval': record.action_type,
            'is_out': int(record.is_out),
            'is_executable': record.is_executable,
            'serve_enabled': record.serve_enabled},
    )

    def render_name(self, record):
        """Render name as a link with a potential flag."""
        # TODO: Move to a template
        render_txt = '<a href="{0}" data-toggle="tooltip" title="{1}">{2}</a>'
        danger_txt = ''
        if record.get_row_all_false_count():
            danger_txt = ugettext(
                'Some users have all conditions equal to FALSE',
            )
        if not record.is_executable:
            danger_txt = ugettext('Some elements in the survey are incomplete')

        if danger_txt:
            render_txt += (
                ' <span class="fa fa-exclamation-triangle"'
                + ' style="color:red;"'
                + ' data-toggle="tooltip"'
                + ' title="{0}"></span>'.format(danger_txt))

        return format_html(
            render_txt,
            reverse('action:edit', kwargs={'pk': record.id}),
            _('Edit the text, conditions and filter'),
            record.name)

    def render_action_type(self, record):
        # TODO: With this solution, there is no possibility to i18n the title
        # in the element (it is done in the JS embedded in the page). Explore
        # using a template.
        return record.action_type

    def render_last_executed_log(self, record):
        """Render the date/time or insert a --- if none"""
        log_item = record.last_executed_log
        return format_html(
            '<a class="spin" href="{0}">{1}</a>',
            reverse('logs:view', kwargs={'pk': log_item.id}),
            simplify_datetime_str(log_item.modified),
        )

    class Meta(object):
        """Define model, fields and ordering."""

        model = Action
        fields = (
            'name',
            'description_text',
            'action_type',
            'last_executed_log',
        )
        sequence = (
            'action_type',
            'name',
            'description_text',
            'last_executed_log',
        )
        exclude = ('content', 'serve_enabled', 'filter')
        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'action-table',
        }


def save_action_form(
    request: HttpRequest,
    form: Union[ActionForm, ActionUpdateForm],
    template_name: str,
) -> JsonResponse:
    """Save information from the form to manipulate condition/filter.

    Function to process JSON POST requests when creating a new action. It
    simply processes name and description and sets the other fields in the
    record.

    :param request: Request object

    :param form: Form to be used in the request/render

    :param template_name: Template for rendering the content

    :return: JSON response
    """
    # Get the corresponding workflow
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse({'html_redirect': reverse('home')})

    resp_data = {}

    # Process the GET request
    if request.method == 'GET' or not form.is_valid():
        resp_data['html_form'] = render_to_string(
            template_name,
            {'form': form},
            request=request)
        return JsonResponse(resp_data)

    # Fill in the fields of the action (without saving to DB)_
    action_item = form.save(commit=False)

    # Process the POST request
    if action_item.action_type == Action.todo_list:
        # To be implemented
        return JsonResponse({'html_redirect': reverse('under_construction')})

    # Is this a new action?
    is_new = action_item.pk is None

    if is_new:  # Action is New. Update user and workflow fields
        action_item.user = request.user
        action_item.workflow = workflow

    # Verify that that action does comply with the name uniqueness
    # property (only with respec to other actions)
    try:
        action_item.save()
        form.save_m2m()  # Propagate the save effect to M2M relations
    except IntegrityError:
        # There is an action with this name already
        form.add_error(
            'name',
            _('An action with that name already exists'))
        resp_data['html_form'] = render_to_string(
            template_name,
            {'form': form},
            request=request)
        return JsonResponse(resp_data)

    # Log the event
    Log.objects.register(
        request.user,
        Log.ACTION_CREATE if is_new else Log.ACTION_UPDATE,
        action_item.workflow,
        {'id': action_item.id,
         'name': action_item.name,
         'workflow_id': workflow.id,
         'workflow_name': workflow.name})

    # Request is correct
    if is_new:
        resp_data['html_redirect'] = reverse(
            'action:edit', kwargs={'pk': action_item.id},
        )
    else:
        resp_data['html_redirect'] = reverse('action:index')

    # Enough said. Respond.
    return JsonResponse(resp_data)


@user_passes_test(is_instructor)
@check_workflow(pf_related='actions')
def action_index(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Process request to show all the actions.

    :param request: HTTP Request

    :param pk: Primary key of the workflow object to use

    :return: HTTP response
    """
    # Reset object to carry action info throughout dialogs
    request.session[action_session_dictionary] = None
    request.session.save()

    return render(
        request,
        'action/index.html',
        {
            'workflow': workflow,
            'table': ActionTable(workflow.actions.all(), orderable=False)
        },
    )


class ActionCreateView(UserIsInstructor, generic.TemplateView):
    """Process get/post requests to create an action."""

    form_class = ActionForm

    template_name = 'action/includes/partial_action_create.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Process the get requet when creating an action."""
        form = self.form_class()
        return save_action_form(
            request,
            form,
            self.template_name)

    def post(self, request: HttpRequest) -> HttpResponse:
        """Process the post request when creating an action."""
        form = self.form_class(request.POST)
        return save_action_form(
            request,
            form,
            self.template_name)


class ActionUpdateView(UserIsInstructor, generic.DetailView):
    """Process the Action Update view.

    @DynamicAttrs
    """

    model = Action

    template_name = 'action/includes/partial_action_update.html'

    context_object_name = 'action'

    form_class = ActionUpdateForm

    def get_object(self, queryset=None) -> Action:
        """Access the Action object being manipulated."""
        act_obj = super().get_object(queryset=queryset)
        if act_obj.workflow.id != self.request.session['ontask_workflow_id']:
            raise Http404()

        return act_obj

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Process the get request."""
        form = self.form_class(instance=self.get_object())
        return save_action_form(
            request,
            form,
            self.template_name)

    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Process post request."""
        form = self.form_class(request.POST, instance=self.get_object())
        return save_action_form(
            request,
            form,
            self.template_name)


# This method only requires the user to be authenticated since it is conceived
#  to serve content that is not only for instructors.


@user_passes_test(is_instructor)
def delete_action(request: HttpRequest, pk: int) -> HttpResponse:
    """Process AJAX request to delete an action.

    :param request: Request object

    :param pk: Action id to delete.

    :return:
    """
    # JSON response object
    resp_data = {}

    # Get the current workflow
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        resp_data['html_redirect'] = reverse('home')
        return JsonResponse(resp_data)

    # Get the appropriate action object
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not action:
        resp_data['html_redirect'] = reverse('home')
        return JsonResponse(resp_data)

    if request.method == 'POST':
        # Log the event
        Log.objects.register(
            request.user,
            Log.ACTION_DELETE,
            action.workflow,
            {'id': action.id,
             'name': action.name,
             'workflow_name': action.workflow.name,
             'workflow_id': action.workflow.id})

        # Perform the delete operation
        action.delete()

        # In this case, the form is valid anyway
        resp_data['html_redirect'] = reverse('action:index')

        return JsonResponse(resp_data)

    resp_data['html_form'] = render_to_string(
        'action/includes/partial_action_delete.html',
        {'action': action},
        request=request)
    return JsonResponse(resp_data)


@user_passes_test(is_instructor)
def edit_action(request: HttpRequest, pk: int) -> HttpResponse:
    """Invoke the specific edit view.

    :param request: Request object
    :param pk: Action PK
    :return: HTML response
    """
    # Try to get the workflow first
    workflow = get_workflow(
        request,
        prefetch_related=['actions', 'columns'])
    if not workflow:
        return redirect('home')

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. '
              + 'Go to "Manage table data" to upload data.'),
        )
        return redirect(reverse('action:index'))

    # Get the action and the columns
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not action:
        messages.error(request, _('Incorrect action request'))
        return redirect('action:index')

    if action.action_type == Action.todo_list:
        return redirect(reverse('under_construction'), {})

    if action.is_out:
        response = edit_action_out(request, workflow, action)
    else:
        response = edit_action_in(request, workflow, action)

    return response
