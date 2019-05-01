# -*- coding: utf-8 -*-

import json
from builtins import object
from typing import Union

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, reverse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views import generic

from action.forms_run import EnableURLForm
from action.ops import (
    clone_action,
)
from action.views_out import (
    action_session_dictionary,
)
from logs.models import Log
from ontask import simplify_datetime_str
from ontask.permissions import UserIsInstructor, is_instructor
from ontask.tables import OperationsColumn
from workflow.ops import get_workflow

from .forms import (
    ActionForm, ActionUpdateForm,
)
from .models import Action


#
# Classes for Table rendering
#
class ActionTable(tables.Table):
    """
    Table to render the list of actions per workflow. The Operations column is
     taken from another class to centralise the customisation.
    """

    name = tables.Column(verbose_name=_('Name'))

    description_text = tables.Column(verbose_name=_('Description'))

    action_type = tables.Column(verbose_name=_('Type'))

    last_executed_log = tables.Column(verbose_name=_('Last executed'))

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
            'serve_enabled': record.serve_enabled}
    )

    def render_name(self, record):
        result = """<a href="{0}" data-toggle="tooltip" title="{1}">{2}</a>"""
        danger_txt = ''
        if record.get_row_all_false_count():
            danger_txt = \
                ugettext('Some users have all conditions equal to FALSE')
        if not record.is_executable:
            danger_txt = \
                ugettext('Some elements in the survey are incomplete')

        if danger_txt:
            result += \
                ' <span class="fa fa-exclamation-triangle"' \
                ' style="color:red;"' \
                ' data-toggle="tooltip"' \
                ' title="{0}"></span>'.format(danger_txt)

        return format_html(result,
                           reverse('action:edit', kwargs={'pk': record.id}),
                           _('Edit the text, conditions and filter'),
                           record.name)

    def render_action_type(self, record):
        return record.action_type

    def render_last_executed_log(self, record):
        log_item = record.last_executed_log
        if not log_item:
            return "---"

        return format_html(
            """<a class="spin" href="{0}">{1}</a>""",
            reverse('logs:view', kwargs={'pk': log_item.id}),
            simplify_datetime_str(log_item.modified)
        )

    class Meta(object):
        model = Action
        fields = ('name', 'description_text', 'action_type',
                  'last_executed_log')
        sequence = ('action_type', 'name', 'description_text',
                    'last_executed_log')
        exclude = ('content', 'serve_enabled', 'filter')
        attrs = {
            'class': 'table table-hover table-bordered shadow',
            'style': 'width: 100%;',
            'id': 'action-table'
        }


class ColumnSelectedTable(tables.Table):
    """
    Table to render the columns selected for a given action in
    """

    column__name = tables.Column(verbose_name=_('Name'))
    column__description_text = tables.Column(
        verbose_name=_('Description (shown to learners)'),
        default='',
    )
    # condition = tables.Column(verbose_name=_('Condition controlling question'))
    condition = tables.Column(
        verbose_name=_('Condition'),
        empty_values=[-1]
    )

    # Template to render the extra column created dynamically
    ops_template = 'action/includes/partial_column_selected_operations.html'

    def __init__(self, *args, **kwargs):
        self.condition_list = kwargs.pop('condition_list')
        super().__init__(*args, **kwargs)

    def render_column__name(self, record):
        return format_html(
            """<a href="#" data-toggle="tooltip" 
                  class="js-workflow-question-edit" data-url="{0}"
                  title="{1}">{2}</a>""",
            reverse('workflow:question_edit',
                    kwargs={'pk': record['column__id']}),
            _('Edit the question'),
            record['column__name']
        )

    def render_condition(self, record):
        return render_to_string(
            'action/includes/partial_column_selected_condition.html',
            {'id': record['id'],
             'cond_selected': record['condition__name'],
             'conditions': self.condition_list
             }
        )

    class Meta(object):
        fields = ('column__id', 'column__name', 'column__description_text',
                  'condition', 'operations')
        sequence = ('column__name', 'column__description_text',
                    'condition',
                    'operations')

        attrs = {
            'class': 'table table-hover table-bordered',
            'style': 'width: 100%;',
            'id': 'column-selected-table'
        }

        row_attrs = {
            'class': lambda record: 'danger' \
                if not record['column__description_text'] else '',
        }


def save_action_form(request, form, template_name):
    """
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
        return JsonResponse({'form_is_valid': True,
                             'html_redirect': reverse('home')})

    # JSON payload
    data = dict()

    # By default, we assume that the POST is not correct.
    data['form_is_valid'] = False

    # Process the GET request
    if request.method == 'GET' or not form.is_valid():
        data['html_form'] = render_to_string(template_name,
                                             {'form': form},
                                             request=request)
        return JsonResponse(data)

    # Fill in the fields of the action (without saving to DB)_
    action_item = form.save(commit=False)

    # Process the POST request
    if action_item.action_type == Action.todo_list:
        # To be implemented
        return JsonResponse(
            {'html_redirect': reverse('under_construction'),
             'form_is_valid': True}
        )

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
        form.add_error('name',
                       _('An action with that name already exists'))
        data['html_form'] = render_to_string(
            template_name,
            {'form': form},
            request=request)
        return JsonResponse(data)

    # Log the event
    Log.objects.register(request.user,
                         Log.ACTION_CREATE if is_new else Log.ACTION_UPDATE,
                         action_item.workflow,
                         {'id': action_item.id,
                          'name': action_item.name,
                          'workflow_id': workflow.id,
                          'workflow_name': workflow.name})

    # Request is correct
    data['form_is_valid'] = True
    if is_new:
        # If a new action is created, jump to the action edit page.
        if action_item.action_type == Action.personalized_text:
            data['html_redirect'] = reverse(
                'action:edit', kwargs={'pk': action_item.id}
            )
        elif action_item.action_type == Action.personalized_canvas_email:
            data['html_redirect'] = reverse(
                'action:edit', kwargs={'pk': action_item.id}
            )
        elif action_item.action_type == Action.personalized_json:
            data['html_redirect'] = reverse(
                'action:edit', kwargs={'pk': action_item.id}
            )
        elif action_item.action_type == Action.survey:
            data['html_redirect'] = reverse(
                'action:edit', kwargs={'pk': action_item.id}
            )
        elif action_item.action_type == Action.todo_list:
            data['html_redirect'] = reverse('action:index')
    else:
        data['html_redirect'] = reverse('action:index')

    # Enough said. Respond.
    return JsonResponse(data)


@user_passes_test(is_instructor)
def action_index_set(request, pk=None):
    """
    Set the workflow in the session object (if not given) and create the page
    with the list of actions.
    :param request: HTTP Request
    :param pk: Primary key of the workflow object to use
    :return: HTTP response
    """

    # Get the appropriate workflow object
    workflow = get_workflow(request,
                            wid=pk,
                            prefetch_related='actions')
    if not workflow:
        return redirect('home')

    # Reset object to carry action info throughout dialogs
    request.session[action_session_dictionary] = {}
    request.session.save()

    qs = workflow.actions.all()

    return render(request,
                  'action/index.html',
                  {'workflow': workflow,
                   'table': ActionTable(qs, orderable=False)}
                  )


class ActionCreateView(UserIsInstructor, generic.TemplateView):
    """
    CBV to handle the create action form (very simple)
    """
    form_class = ActionForm
    template_name = 'action/includes/partial_action_create.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return save_action_form(request,
                                form,
                                self.template_name)

    def post(self, request):
        form = self.form_class(request.POST)
        return save_action_form(request,
                                form,
                                self.template_name)


class ActionUpdateView(UserIsInstructor, generic.DetailView):
    """
    CBV to handle the update (as in name and description) action.
    @DynamicAttrs
    """
    model = Action
    template_name = 'action/includes/partial_action_update.html'
    context_object_name = 'action'
    form_class = ActionUpdateForm

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.workflow.id != self.request.session['ontask_workflow_id']:
            raise Http404()

        return obj

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.get_object())
        return save_action_form(request,
                                form,
                                self.template_name)

    def post(self, request, **kwargs):
        form = self.form_class(request.POST, instance=self.get_object())
        return save_action_form(request,
                                form,
                                self.template_name)


@user_passes_test(is_instructor)
def showurl(request, pk):
    """
    Function that given a JSON request with an action pk returns the URL used
    to retrieve the personalised message.
    :param request: Json request
    :param pk: Primary key of the action to show the URL
    :return: Json response with the content to show in the screen
    """

    # AJAX result
    data = {'form_is_valid': False}

    # Get the current workflow
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('home')
        return JsonResponse(data)

    # Get the action object
    action = workflow.actions.filter(
        pk=pk
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user)
    ).first()
    if not action:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('home')
        return JsonResponse(data)

    form = EnableURLForm(request.POST or None, instance=action)

    if request.method == 'POST' and form.is_valid():
        if form.has_changed():
            # Reflect the change in the action element
            form.save()

            # Recording the event
            Log.objects.register(request.user,
                                 Log.ACTION_SERVE_TOGGLED,
                                 action.workflow,
                                 {'id': action.id,
                                  'name': action.name,
                                  'serve_enabled': action.serve_enabled})

        data['form_is_valid'] = True
        data['html_redirect'] = reverse('action:index')
        return JsonResponse(data)

    # Create the text for the action
    url_text = reverse('action:serve', kwargs={'action_id': action.pk})

    # Render the page with the abolute URI
    data['html_form'] = render_to_string(
        'action/includes/partial_action_showurl.html',
        {'url_text': request.build_absolute_uri(url_text),
         'form': form,
         'action': action},
        request=request)

    return JsonResponse(data)


# This method only requires the user to be authenticated since it is conceived
#  to serve content that is not only for instructors.


@user_passes_test(is_instructor)
def delete_action(request, pk):
    """
    View to handle the AJAX form to delete an action.
    :param request: Request object
    :param pk: Action id to delete.
    :return:
    """

    # JSON response object
    data = dict()

    # Get the current workflow
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('home')
        return JsonResponse(data)

    # Get the appropriate action object
    action = workflow.actions.filter(
        pk=pk
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user)
    ).first()
    if not action:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('home')
        return JsonResponse(data)

    if request.method == 'POST':
        # Log the event
        Log.objects.register(request.user,
                             Log.ACTION_DELETE,
                             action.workflow,
                             {'id': action.id,
                              'name': action.name,
                              'workflow_name': action.workflow.name,
                              'workflow_id': action.workflow.id})

        # Perform the delete operation
        action.delete()

        # In this case, the form is valid anyway
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('action:index')

        return JsonResponse(data)

    data['html_form'] = render_to_string(
        'action/includes/partial_action_delete.html',
        {'action': action},
        request=request)
    return JsonResponse(data)


@user_passes_test(is_instructor)
def clone(request: HttpRequest, pk: int) -> JsonResponse:
    """View to clone an action.

    :param request: Request object
    :param pk: id of the action to clone
    :return:
    """
    # JSON response
    data_resp = {}

    # Get the current workflow
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        data_resp['form_is_valid'] = True
        data_resp['html_redirect'] = reverse('home')
        return JsonResponse(data_resp)

    # Initial data in the context
    data_resp['form_is_valid'] = False
    context = {'pk': pk}  # For rendering

    # Get the action
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not action:
        data_resp['form_is_valid'] = True
        data_resp['html_redirect'] = reverse('action:index')
        return JsonResponse(data_resp)

    # Get the name of the action to clone
    context['name'] = action.name

    if request.method == 'GET':
        data_resp['html_form'] = render_to_string(
            'action/includes/partial_action_clone.html',
            context,
            request=request)
        return JsonResponse(data_resp)

    # POST REQUEST!
    # Get the new name appending as many times as needed the 'Copy of '
    new_name = 'Copy of ' + action.name
    while workflow.actions.filter(name=new_name).exists():
        new_name = 'Copy of ' + new_name

    old_id = action.id
    old_name = action.name
    action = clone_action(action, new_workflow=None, new_name=new_name)

    # Log event
    Log.objects.register(
        request.user,
        Log.ACTION_CLONE,
        workflow,
        {'id_old': old_id,
         'id_new': action.id,
         'name_old': old_name,
         'name_new': action.name})
    data_resp['form_is_valid'] = True
    data_resp['html_redirect'] = reverse('action:index')

    messages.success(
        request,
        'Action successfully cloned.')

    return redirect(reverse('action:index'))


@user_passes_test(is_instructor)
def timeline(request: HttpRequest, pk=Union[None, int]) -> HttpResponse:
    """Show a vertical timeline of action executions.

    :param request: HTTP request
    :param pk: Action PK. If none, all of them are considered
    :return: HTTP response
    """
    # Get the workflow first
    workflow = get_workflow(request, prefetch_related='logs')
    if not workflow:
        return redirect('home')

    action = None
    if pk:
        action = workflow.actions.filter(pk=pk).first()
        if not action:
            # The action is not part of the selected workflow
            return redirect('home')

    event_names = [
        Log.SCHEDULE_EMAIL_EXECUTE,
        Log.DOWNLOAD_ZIP_ACTION,
        Log.SCHEDULE_JSON_EXECUTE,
        Log.SCHEDULE_CANVAS_EMAIL_EXECUTE,
        Log.SCHEDULE_EMAIL_EDIT,
        Log.SCHEDULE_JSON_EDIT,
        Log.SCHEDULE_CANVAS_EMAIL_EXECUTE]

    if action:
        logs = workflow.logs.filter(payload__action_id=action.id)
    else:
        logs = workflow.logs.all()

    # Filter the logs to display and transform into values (process the json
    # and the long value for the log name
    logs = [
        {'id': log.id,
         'name': log.get_name_display(),
         'modified': log.modified,
         'payload': json.dumps(log.payload, indent=2),
         'action_name': log.payload['action'],
         'action_id': log.payload['action_id']}
        for log in logs.filter(name__in=event_names)
    ]

    return render(
        request,
        'action/timeline.html',
        {'event_list': logs, 'action': action})


@login_required
def thanks(request: HttpRequest) -> HttpResponse:
    """Responde simply saying thanks.

    :param request: Http requst
    :return: Http response
    """
    return render(request, 'thanks.html', {})
