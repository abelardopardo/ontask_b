# -*- coding: utf-8 -*-

"""Views to render the list of actions."""

from typing import Optional, Union

import django_tables2 as tables
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from ontask import simplify_datetime_str
from ontask.action.forms import ActionForm, ActionUpdateForm
from ontask.action.payloads import set_action_payload
from ontask.action.views.edit_personalized import edit_action_out
from ontask.action.views.edit_rubric import edit_action_rubric
from ontask.action.views.edit_survey import edit_action_in
from ontask.core.decorators import ajax_required, get_action, get_workflow
from ontask.core.permissions import UserIsInstructor, is_instructor
from ontask.core.tables import OperationsColumn
from ontask.core.views import under_construction
from ontask.models import Action, Log, Workflow


class ActionTable(tables.Table):
    """Class to render the list of actions per workflow.

    The Operations column is taken from another class to centralise the
    customisation.
    """

    name = tables.Column(verbose_name=_('Name'))

    description_text = tables.Column(verbose_name=_('Description'))

    action_type = tables.TemplateColumn(
        template_name='action/includes/partial_action_type.html',
        verbose_name=_('Type'))

    last_executed_log = tables.LinkColumn(
        verbose_name=_('Last executed'),
        empty_values=['', None],
        viewname='logs:view',
        text=lambda record: simplify_datetime_str(
            record.last_executed_log.modified),
        kwargs={'pk': tables.A('last_executed_log.id')},
        attrs={'a': {'class': 'spin'}},
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
        return render_to_string(
            'action/includes/partial_action_name.html',
            context={
                'action_id': record.id,
                'danger_msg': (
                    record.get_row_all_false_count or not record.is_executable
                ),
                'action_name': record.name,
            },
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
    workflow: Optional[Workflow] = None,
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
    if request.method == 'POST' and form.is_valid():

        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

        if Action.TODO_LIST == form.cleaned_data.get('action_type'):
            # To be implemented
            return JsonResponse(
                {'html_redirect': reverse('under_construction')})

        # Fill in the fields of the action (without saving to DB)_
        action_item = form.save(commit=False)

        if action_item.pk is None:
            # Action is New. Update certain vars
            action_item.workflow = workflow
            action_item.save()
            log_type = Log.ACTION_CREATE
            return_url = reverse('action:edit', kwargs={'pk': action_item.id})
        else:
            action_item.save()
            log_type = Log.ACTION_UPDATE
            return_url = reverse('action:index')

        action_item.log(request.user, log_type)
        return JsonResponse({'html_redirect': return_url})

    return JsonResponse({
        'html_form': render_to_string(
            template_name,
            {'form': form},
            request=request),
    })


@user_passes_test(is_instructor)
@get_workflow(pf_related='actions')
def action_index(
    request: HttpRequest,
    wid: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Show all the actions attached to the workflow.

    :param request: HTTP Request

    :param pk: Primary key of the workflow object to use

    :return: HTTP response
    """
    # Reset object to carry action info throughout dialogs
    set_action_payload(request.session)
    request.session.save()

    return render(
        request,
        'action/index.html',
        {
            'workflow': workflow,
            'table': ActionTable(workflow.actions.all(), orderable=False),
        },
    )


class ActionCreateView(UserIsInstructor, generic.TemplateView):
    """Process get/post requests to create an action."""

    form_class = ActionForm

    template_name = 'action/includes/partial_action_create.html'

    @method_decorator(user_passes_test(is_instructor))
    @method_decorator(ajax_required)
    @method_decorator(get_workflow())
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Process the get requet when creating an action."""
        return save_action_form(
            request,
            self.form_class(workflow=kwargs.get('workflow')),
            self.template_name,
            workflow=kwargs.get('workflow'),
        )

    @method_decorator(user_passes_test(is_instructor))
    @method_decorator(ajax_required)
    @method_decorator(get_workflow())
    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Process the post request when creating an action."""
        return save_action_form(
            request,
            self.form_class(request.POST, workflow=kwargs.get('workflow')),
            self.template_name,
            workflow=kwargs.get('workflow'),
        )


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

    @method_decorator(user_passes_test(is_instructor))
    @method_decorator(ajax_required)
    @method_decorator(get_workflow())
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Process the get request."""
        return save_action_form(
            request,
            self.form_class(
                instance=self.get_object(),
                workflow=kwargs['workflow']),
            self.template_name)

    @method_decorator(user_passes_test(is_instructor))
    @method_decorator(ajax_required)
    @method_decorator(get_workflow())
    def post(self, request: HttpRequest, **kwargs) -> HttpResponse:
        """Process post request."""
        return save_action_form(
            request,
            self.form_class(
                request.POST,
                instance=self.get_object(),
                workflow=kwargs['workflow'],
            ),
            self.template_name)


@user_passes_test(is_instructor)
@get_action(pf_related=['actions', 'columns'])
def edit_action(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> HttpResponse:
    """Invoke the specific edit view.

    :param request: Request object
    :param pk: Action PK
    :return: HTML response
    """
    edit_function_dict = {
        Action.PERSONALIZED_TEXT: edit_action_out,
        Action.PERSONALIZED_CANVAS_EMAIL: edit_action_out,
        Action.PERSONALIZED_JSON: edit_action_out,
        Action.RUBRIC_TEXT: edit_action_rubric,
        Action.SEND_LIST: edit_action_out,
        Action.SEND_LIST_JSON: edit_action_out,
        Action.SURVEY: edit_action_in,
        Action.TODO_LIST: under_construction,
    }

    return edit_function_dict[action.action_type](request, workflow, action)


@user_passes_test(is_instructor)
@ajax_required
@get_action()
def delete_action(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    action: Optional[Action] = None,
) -> JsonResponse:
    """Process AJAX request to delete an action.

    :param request: Request object

    :param pk: Action id to delete.

    :return:
    """
    # JSON response object
    # Get the appropriate action object
    if request.method == 'POST':
        action.log(request.user, Log.ACTION_DELETE)
        action.delete()
        return JsonResponse({'html_redirect': reverse('action:index')})

    return JsonResponse({
        'html_form': render_to_string(
            'action/includes/partial_action_delete.html',
            {'action': action},
            request=request),
    })
