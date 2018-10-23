# -*- coding: utf-8 -*-


from future import standard_library
standard_library.install_aliases()
from builtins import next
from builtins import object
import pytz
from django.db import IntegrityError
from django.utils.html import format_html

from action.views_out import session_dictionary_name
from logs.models import Log
from visualizations.plotly import PlotlyHandler

import urllib.parse
from urllib.parse import urlencode

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, reverse, render
from django.template.loader import render_to_string
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from action.evaluate import render_template
from dataops import ops, pandas_db
from ontask.permissions import UserIsInstructor, is_instructor
from ontask.tables import OperationsColumn
from workflow.ops import get_workflow
from .forms import (
    ActionUpdateForm,
    ActionForm,
    EditActionOutForm,
    EnableURLForm,
    ActionDescriptionForm, ActionImportForm
)
from action.ops import (
    serve_action_in,
    serve_action_out,
    clone_action,
    do_export_action,
    do_import_action,
    get_workflow_action)
from .models import Action, Condition


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

    operations = OperationsColumn(
        verbose_name=_('Operations'),
        template_file='action/includes/partial_action_operations.html',
        template_context=lambda record: {
            'id': record['id'],
            'action_tval': record['action_tval'],
            'is_out': int(record['is_out']),
            'is_executable': record['is_executable'],
            'serve_enabled': record['serve_enabled']}
    )

    def render_last_executed_log(self, record):
        log_item = record['last_executed_log']
        if not log_item:
            return "---"

        return format_html(
            """<a class="spin" href="{0}">{1}</a>""".format(
                reverse('logs:view', kwargs={'pk': log_item.id}),
                log_item.modified.astimezone(
                    pytz.timezone(settings.TIME_ZONE)
                )
            )
        )

    class Meta(object):
        model = Action

        fields = ('name', 'description_text', 'action_type',
                  'last_executed_log')

        sequence = ('name', 'description_text', 'action_type',
                    'last_executed_log')

        exclude = ('content', 'serve_enabled', 'columns', 'filter')

        attrs = {
            'class': 'table display table-bordered',
            'id': 'action-table'
        }

        row_attrs = {
            'style': 'text-align:center;',
        }


class ColumnSelectedTable(tables.Table):
    """
    Table to render the columns selected for a given action in
    """
    name = tables.Column(verbose_name=_('Name'))
    description_text = tables.Column(
        verbose_name=_('Description (shown to learners)'),
        default='',
    )

    # Template to render the extra column created dynamically
    ops_template = 'action/includes/partial_column_selected_operations.html'

    class Meta(object):
        fields = ('name', 'description_text', 'operations')
        attrs = {
            'class': 'table display table-bordered',
            'id': 'column-selected-table'
        }

        row_attrs = {
            'style': 'text-align:center;',
            'class': lambda record:
            'danger' if not record['description_text'] else '',
        }


def save_action_form(request, form, template_name):
    """
    Function to process JSON POST requests when creating a new action. It
    simply processes name and description and sets the other fields in the
    record.
    :param request: Request object
    :param form: Form to be used in the request/render
    :param action_type: Type of action
    :param template_name: Template for rendering the content
    :return: JSON response
    """

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

    # Process the POST request
    if form.cleaned_data['action_type'] == Action.TODO_LIST:
        # To be implemented
        return JsonResponse(
            {'html_redirect': reverse('under_construction'),
             'form_is_valid': True}
        )

    # Fill in the fields of the action (without saving to DB)_
    action_item = form.save(commit=False)

    # Is this a new action?
    is_new = action_item.pk is None

    # Get the corresponding workflow
    workflow = get_workflow(request)
    if not workflow:
        redirect('workflow:index')

    if is_new:  # Action is New. Update user and workflow fields
        action_item.user = request.user
        action_item.workflow = workflow

    # Verify that that action does comply with the name uniqueness
    # property (only with respec to other actions)
    try:
        action_item.save()
        form.save_m2m()  # Propagate the save effect to M2M relations
    except IntegrityError as e:
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
        if action_item.action_type == Action.PERSONALIZED_TEXT:
            data['html_redirect'] = reverse(
                'action:edit', kwargs={'pk': action_item.id}
            )
        elif action_item.action_type == Action.PERSONALIZED_JSON:
            data['html_redirect'] = reverse(
                'action:edit', kwargs={'pk': action_item.id}
            )
        elif action_item.action_type == Action.SURVEY:
            data['html_redirect'] = reverse(
                'action:edit', kwargs={'pk': action_item.id}
            )
        elif action_item.action_type == Action.TODO_LIST:
            data['html_redirect'] = reverse('action:index')
    else:
        data['html_redirect'] = reverse('action:index')

    # Enough said. Respond.
    return JsonResponse(data)


@user_passes_test(is_instructor)
def action_index(request):
    """
    Render the list of actions attached to a workflow.
    :param request: Request object
    :return: HTTP response with the table.
    """

    # Get the appropriate workflow object
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Reset object to carry action info throughout dialogs
    request.session[session_dictionary_name] = {}
    request.session.save()

    # Get the actions
    actions = Action.objects.filter(workflow__id=workflow.id)

    # Context to render the template
    context = {'has_table': ops.workflow_has_table(workflow)}

    # Build the table only if there is anything to show (prevent empty table)
    qset = []
    for action in actions:
        qset.append({'id': action.id,
                     'name': action.name,
                     'description_text': action.description_text,
                     'action_type': action.get_action_type_display(),
                     'action_tval': action.action_type,
                     'is_out': action.is_out,
                     'is_executable': action.is_executable,
                     'last_executed_log': action.last_executed_log,
                     'serve_enabled': action.serve_enabled})

    context['table'] = \
        ActionTable(qset, orderable=False)
    context['no_actions'] = len(qset) == 0

    return render(request, 'action/index.html', context)


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
        obj = super(ActionUpdateView, self).get_object(queryset=queryset)
        if obj.workflow.id != self.request.session['ontask_workflow_id']:
            raise Http404()

        return obj

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=Action.objects.get(pk=kwargs['pk']))
        return save_action_form(request,
                                form,
                                self.template_name)

    def post(self, request, **kwargs):
        form = self.form_class(request.POST,
                               instance=Action.objects.get(pk=kwargs['pk']))
        return save_action_form(request,
                                form,
                                self.template_name)


@user_passes_test(is_instructor)
def edit_description(request, pk):
    """
    Edit the description attached to an action

    :param request: AJAX request
    :param pk: Action ID
    :return: AJAX response
    """

    # Try to get the workflow first
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse({'form_is_valid': True,
                             'html_redirect': reverse('workflow:index')})

    # Get the action
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)).distinct().get(pk=pk)
    except ObjectDoesNotExist:
        return JsonResponse({'form_is_valid': True,
                             'html_redirect': reverse('action:index')})

    # Initial result. In principle, re-render page
    data = {'form_is_valid': False}

    # Create the form
    form = ActionDescriptionForm(request.POST or None,
                                 instance=action)

    # Process the POST
    if request.method == 'POST' and form.is_valid():
        # Save item in the DB
        action.save()

        # Log the event
        Log.objects.register(request.user,
                             Log.ACTION_UPDATE,
                             action.workflow,
                             {'id': action.id,
                              'name': action.name,
                              'workflow_id': workflow.id,
                              'workflow_name': workflow.name})

        # Request is correct
        data['form_is_valid'] = True
        data['html_redirect'] = ''

        # Enough said. Respond.
        return JsonResponse(data)

    data['html_form'] = render_to_string(
        'action/includes/partial_action_edit_description.html',
        {'form': form, 'action': action},
        request=request)

    return JsonResponse(data)


@user_passes_test(is_instructor)
@csrf_exempt
def action_out_save_content(request, pk):
    """

    :param request: HTTP request (POST)
    :param pk: Action ID
    :return: Nothing, changes reflected in the DB
    """

    # Try to get the workflow first
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse({})

    # Get the action
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)).distinct().get(pk=pk)
    except ObjectDoesNotExist:
        return JsonResponse({})

    # Wrong type of action.
    if action.is_in:
        return JsonResponse({})

    # If the request has the 'action_content', update the action
    action_content = request.POST.get('action_content', None)
    if action_content:
        action.set_content(action_content)
        action.save()

    return JsonResponse({})


@user_passes_test(is_instructor)
def edit_action(request, pk):
    """
    View to select the right action edit procedure
    :param request: Request object
    :param pk: Action PK
    :return: HTML response
    """

    # Try to get the workflow first
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. Go to "Manage table data" to upload data.')
        )
        return redirect(reverse('action:index'))

    # Get the action and the columns
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)
        ).distinct().prefetch_related('columns').get(pk=pk)
    except ObjectDoesNotExist:
        return redirect('action:index')

    if action.action_type == Action.PERSONALIZED_TEXT:
        return edit_action_out(request, workflow, action)

    if action.action_type == Action.PERSONALIZED_JSON:
        return edit_action_out(request, workflow, action)

    if action.action_type == Action.SURVEY:
        return edit_action_in(request, workflow, action)

    if action.action_type == Action.TODO_LIST:
        return redirect(reverse('under_construction'), {})
        # return edit_action_in(request, workflow, action)


def edit_action_out(request, workflow, action):
    """
    View to handle the form to edit an action OUT (editor, conditions,
    filters, etc).
    :param request: Request object
    :param action: Action
    :return: HTML response
    """

    # Create the form
    form = EditActionOutForm(request.POST or None, instance=action)

    # Get the filter or None
    filter_condition = action.get_filter()

    # Conditions to show in the page.
    conditions = Condition.objects.filter(
        action=action, is_filter=False
    ).order_by('created')

    # Context to render the form
    context = {'filter_condition': filter_condition,
               'action': action,
               'conditions': conditions,
               'query_builder_ops': workflow.get_query_builder_ops_as_str(),
               'attribute_names': [x for x in list(workflow.attributes.keys())],
               'column_names': workflow.get_column_names(),
               'selected_rows':
                   filter_condition.n_rows_selected if filter_condition else -1,
               'has_data': ops.workflow_has_table(action.workflow),
               'total_rows': workflow.nrows,
               'form': form,
               'vis_scripts': PlotlyHandler.get_engine_scripts()
               }

    # Template to use
    template = 'action/edit_personalized_text.html'
    if action.action_type == Action.PERSONALIZED_JSON:
        template = 'action/edit_personalized_json.html'

    # Processing the request after receiving the text from the editor
    if request.method == 'GET' or not form.is_valid():
        # Return the same form in the same page
        return render(request, template, context=context)

    # Get content
    content = form.cleaned_data.get('content', None)

    # Render the content as a template and catch potential problems.
    # This seems to be only possible if dealing directly with Jinja2
    # instead of Django.
    try:
        render_template(content, {}, action)
    except Exception as e:
        # Pass the django exception to the form (fingers crossed)
        form.add_error(None, e.message)
        return render(request, template, context)

    # Log the event
    Log.objects.register(request.user,
                         Log.ACTION_UPDATE,
                         action.workflow,
                         {'id': action.id,
                          'name': action.name,
                          'workflow_id': workflow.id,
                          'workflow_name': workflow.name,
                          'content': content})

    # Text is good. Update the content of the action
    action.set_content(content)

    # Update additional fields
    if action.action_type == Action.PERSONALIZED_JSON:
        action.target_url = form.cleaned_data['target_url']

    action.save()

    return redirect('action:index')


def edit_action_in(request, workflow, action):
    """
    View to handle the AJAX form to edit an action in (filter + columns).
    :param request: Request object
    :param workflow: workflow
    :param action: Action
    :return: HTTP response
    """

    # Get filter or None
    filter_condition = action.get_filter()

    # Get the number of rows in DF selected by filter.
    if filter_condition:
        filter_condition.n_rows_selected = \
            pandas_db.num_rows(action.workflow.id, filter_condition.formula)
        filter_condition.save()

    # Column names suitable to insert
    columns_selected = action.columns.filter(is_key=False).order_by('position')
    columns_to_insert = [c for c in workflow.columns.all()
                         if not c.is_key and c not in columns_selected]

    # Has key column and has no-key column
    has_no_key = action.columns.filter(is_key=False).exists()
    has_empty_description = columns_selected.filter(
        description_text=''
    ).exists()

    # Create the context info.
    ctx = {'action': action,
           'filter_condition': filter_condition,
           'selected_rows':
               filter_condition.n_rows_selected if filter_condition else -1,
           'total_rows': workflow.nrows,
           'query_builder_ops': workflow.get_query_builder_ops_as_str(),
           'has_data': ops.workflow_has_table(action.workflow),
           'key_selected': action.columns.filter(is_key=True).first(),
           'columns_to_insert': columns_to_insert,
           'column_selected_table': ColumnSelectedTable(
               columns_selected.values('id', 'name', 'description_text'),
               orderable=False,
               extra_columns=[
                   ('operations',
                    OperationsColumn(
                        verbose_name='Ops',
                        template_file=ColumnSelectedTable.ops_template,
                        template_context=lambda record: {'id': record['id'],
                                                         'aid': action.id})
                    )]
           ),
           'has_no_key': has_no_key,
           'has_empty_description': has_empty_description}

    return render(request, 'action/edit_in.html', ctx)


@user_passes_test(is_instructor)
def export_ask(request, pk):
    """
    Function that asks for confirmation before exporting an action
    :param request: HTTP request
    :param pk: Action ID
    :return: HTTP response to the next page where the export is done
    """

    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    action = Action.objects.filter(pk=pk).first()
    if not action:
        return redirect('action:index')

    # GET request, simply render the form
    return render(request,
                  'action/export_ask.html',
                  {'action': action,
                   'cnames': [c.name for c in action.columns.all()]})


@user_passes_test(is_instructor)
def export_done(request, pk):
    """
    This request exports the action pointed by the pk
    :param request:
    :param pk: Unique key of the action to export
    :return: HTTP response
    """

    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    action = Action.objects.filter(pk=pk).first()
    if not action:
        return redirect('action:index')

    return render(request, 'action/export_done.html', {'action': action})


@user_passes_test(is_instructor)
def export_download(request, pk):
    """
    This request exports the action pointed by the pk
    :param request:
    :param pk: Unique key of the action to export
    :return: HTTP response
    """

    # Get the workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    action = Action.objects.filter(pk=pk).first()
    if not action:
        return redirect('action:index')

    response = do_export_action(action)

    return response


@user_passes_test(is_instructor)
def action_import(request):
    """
    This request imports one action given in a gz file
    :param request: Http request
    :return: HTTP response
    """

    # Get workflow
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    form = ActionImportForm(request.POST or None, request.FILES or None)

    context = {'form': form}

    # If a get request or the form is not valid, render the page.
    if request.method == 'GET' or not form.is_valid():
        return render(request, 'action/import.html', context)

    new_action_name = form.cleaned_data['name']
    if Action.objects.filter(
            workflow=workflow,
            workflow__user=request.user,
            name=new_action_name).exists():
        # There is an action with this name. Return error.
        form.add_error(None, _('An action with this name already exists'))
        return render(request, 'action/import.html', context)

    # Process the reception of the file
    if not form.is_multipart():
        form.add_error(None, _('Incorrect form request (it is not multipart)'))
        return render(request, 'action/import.html', context)

    # UPLOAD THE FILE!
    status = do_import_action(request.user,
                              workflow,
                              form.cleaned_data['name'],
                              request.FILES['file'])

    # If something went wrong, show at to the top of the page
    if status:
        messages.error(request, status)

    # Go back to the list of actions
    return redirect('action:index')


@user_passes_test(is_instructor)
def select_column_action(request, apk, cpk, key=None):
    """
    Operation to add a column to action in
    :param request: Request object
    :param apk: Action PK
    :param cpk: column PK
    :param key: The columns is a key column
    :return: JSON response
    """
    # Check if the workflow is locked
    workflow = get_workflow(request)
    if not workflow:
        return reverse('workflow:index')

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. Go to "Manage table data" to upload data.')
        )
        return JsonResponse({'html_redirect': reverse('action:index')})

    # Get the action and the columns
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)
        ).distinct().prefetch_related('columns').get(pk=apk)
    except ObjectDoesNotExist:
        return JsonResponse({'html_redirect': reverse('action:index')})

    # Get the column
    try:
        column = action.workflow.columns.get(pk=cpk)
    except ObjectDoesNotExist:
        return JsonResponse({'html_redirect': reverse('action:index')})

    # Parameters are correct, so add the column to the action.
    if key:
        current_key = action.columns.filter(is_key=True).first()
        if current_key:
            # Remove the existing one
            action.columns.remove(current_key)
        if column.is_key:
            action.columns.add(column)
        return JsonResponse({'html_redirect': ''})

    action.columns.add(column)
    # Refresh the page to show the column in the list.
    return JsonResponse({'html_redirect': ''})


@user_passes_test(is_instructor)
def unselect_column_action(request, apk, cpk):
    """
    Operation to drop a column from action in
    :param request: Request object
    :param apk: Action PK
    :param cpk: column PK
    :return: JSON response
    """
    # Check if the workflow is locked
    workflow = get_workflow(request)
    if not workflow:
        return reverse('workflow:index')

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. Go to "Manage table data" to upload data.')
        )
        return redirect(reverse('action:index'))

    # Get the action and the columns
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)
        ).distinct().prefetch_related('columns').get(pk=apk)
    except ObjectDoesNotExist:
        return redirect(reverse('action:index'))

    # Get the column
    try:
        column = action.workflow.columns.get(pk=cpk)
    except ObjectDoesNotExist:
        return redirect(reverse('action:index'))

    # Parameters are correct, so add the column to the action.
    action.columns.remove(column)

    return redirect(reverse('action:edit', kwargs={'pk': action.id}))


@user_passes_test(is_instructor)
def shuffle_questions(request, pk):
    """
    Operation to drop a column from action in
    :param request: Request object
    :param pk: Action PK
    :return: HTML response
    """

    # Check if the workflow is locked
    workflow = get_workflow(request)
    if not workflow:
        return reverse('workflow:index')

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. Go to "Manage table data" to upload data.')
        )
        return redirect(reverse('action:index'))

    # Get the action and the columns
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)
        ).distinct().prefetch_related('columns').get(pk=pk)
    except ObjectDoesNotExist:
        return redirect(reverse('action:index'))

    action.shuffle = not action.shuffle
    action.save()

    return JsonResponse({'shuffle': action.shuffle})


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

    # Get the action object
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)).distinct().get(pk=pk)
    except Action.DoesNotExist:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
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
@csrf_exempt
@xframe_options_exempt
@login_required
def serve(request, action_id):
    """
    View to serve the rendering of an action in a workflow for a given user.

    - uatn: User attribute name. The attribute to check for authentication.
      By default this will be "email".

    - uatv: User attribute value. The value to check with respect to the
      previous attribute. The default is the user attached to the request.

    If the two last parameters are given, the authentication is done as:

    user_record[user_attribute_name] == user_attribute_value

    :param request:
    :param action_id: Action ID to use
    :return:
    """

    # Get the param dicts
    if request.method == 'POST':
        params = request.POST
    else:
        params = request.GET

    # Get the parameters
    user_attribute_name = params.get('uatn', 'email')

    # Get the action object
    try:
        action = Action.objects.get(pk=int(action_id))
    except ObjectDoesNotExist:
        raise Http404

    # If it is not enabled, reject the request
    if not action.serve_enabled:
        raise Http404

    # If it is enabled but not active (date/time)
    if not action.is_active:
        raise Http404

    if action.is_out:
        return serve_action_out(request.user, action, user_attribute_name)

    return serve_action_in(request, action, user_attribute_name, False)


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

    # Get the appropriate action object
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)).distinct().get(pk=pk)
    except (KeyError, ObjectDoesNotExist):
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
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
def run_action_in(request, pk):
    """
    Function that runs the action in. Mainly, it renders a table with
    all rows that satisfy the filter condition and includes a link to
    enter data for each of them.

    :param request:
    :param pk: Action id. It is assumed to be an action In
    :return:
    """

    # Get the workflow and action
    wflow_action = get_workflow_action(request, pk)

    # If nothing found, return
    if not wflow_action:
        return redirect(reverse('action:index'))

    # Extract workflow and action
    workflow, action = wflow_action

    if action.action_type != Action.SURVEY and \
            action.action_type != Action.TODO_LIST:
        # Incorrect type of action.
        return redirect(reverse('action:index'))

    # Render template with active columns.
    return render(request,
                  'action/run_survey.html',
                  {'columns': [c for c in action.columns.all() if c.is_active],
                   'action': action})


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
def run_survey_ss(request, pk):
    """
    Serve the AJAX requests to show the elements in the table that satisfy
    the filter and between the given limits.
    :param request:
    :param pk: action id being run
    :return:
    """

    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')}
        )

    # If there is not DF, go to workflow details.
    if not ops.workflow_id_has_table(workflow.id):
        return JsonResponse({'error': _('There is no data in the table')})

    # Get the action
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)).distinct().get(pk=pk)
    except ObjectDoesNotExist:
        return redirect('action:index')

    # Check that the GET parameter are correctly given
    try:
        draw = int(request.POST.get('draw', None))
        start = int(request.POST.get('start', None))
        length = int(request.POST.get('length', None))
        order_col = request.POST.get('order[0][column]', None)
        order_dir = request.POST.get('order[0][dir]', 'asc')
    except ValueError:
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')}
        )

    # Get the column information from the request and the rest of values.
    search_value = request.POST.get('search[value]', None)

    # Get columns and the position of the first key
    columns = action.columns.all()
    column_names = [x.name for x in columns]
    key_idx = next(idx for idx, c in enumerate(columns) if c.is_key)

    # See if an order column has been given.
    if order_col:
        order_col = columns[int(order_col)]

    # Get the search pairs of field, value
    cv_tuples = []
    if search_value:
        cv_tuples = [(c.name, search_value, c.data_type) for c in columns]

    # Filter
    cfilter = action.get_filter()

    # Get the query set (including the filter in the action)
    qs = pandas_db.search_table_rows(
        workflow.id,
        cv_tuples,
        True,
        order_col.name,
        order_dir == 'asc',
        column_names,  # Column names in the action
        cfilter.formula if cfilter else None
    )

    # Post processing + adding operations
    final_qs = []
    items = 0
    for row in qs[start:start + length]:
        items += 1

        # Render the first element (the key) as the link to the page to update
        # the content.
        dst_url = reverse('action:run_survey_row', kwargs={'pk': action.id})
        url_parts = list(urllib.parse.urlparse(dst_url))
        query = dict(urllib.parse.parse_qs(url_parts[4]))
        query.update({'uatn': column_names[key_idx], 'uatv': row[key_idx]})
        url_parts[4] = urlencode(query)
        link_item = '<a href="{0}">{1}</a>'.format(
            urllib.parse.urlunparse(url_parts), row[key_idx]
        )
        row = list(row)
        row[key_idx] = link_item

        # Add the row for rendering
        final_qs.append(row)

        if items == length:
            # We reached the number or requested elements, abandon loop
            break

    data = {
        'draw': draw,
        'recordsTotal': workflow.nrows,
        'recordsFiltered': len(qs),
        'data': final_qs
    }

    return JsonResponse(data)


@user_passes_test(is_instructor)
def run_survey_row(request, pk):
    """
    Function that runs the action in for a single row. The request
    must have query parameters uatn = key name and uatv = key value to
    perform the lookup.

    :param request:
    :param pk: Action id. It is assumed to be an action In
    :return:
    """

    # Get the workflow first
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. Go to "Manage table data" to upload data.')
        )
        return redirect(reverse('action:index'))

    # Get the action
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)).distinct().get(pk=pk)
    except ObjectDoesNotExist:
        return redirect('action:index')

    # If the action is an "out" action, return to index
    if action.is_out:
        return redirect('action:index')

    # Get the parameters
    user_attribute_name = request.GET.get('uatn', 'email')

    return serve_action_in(request, action, user_attribute_name, True)


@user_passes_test(is_instructor)
def clone(request, pk):
    """
    View to clone an action
    :param request: Request object
    :param pk: id of the action to clone
    :return:
    """

    # JSON response
    data = dict()

    # Get the current workflow
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    # Initial data in the context
    data['form_is_valid'] = False
    context = {'pk': pk}  # For rendering

    # Get the action
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)).distinct().get(pk=pk)
    except ObjectDoesNotExist:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('action:index')
        return JsonResponse(data)

    # Get the name of the action to clone
    context['name'] = action.name

    if request.method == 'GET':
        data['html_form'] = render_to_string(
            'action/includes/partial_action_clone.html',
            context,
            request=request)
        return JsonResponse(data)

    # POST REQUEST!

    # Get the new name appending as many times as needed the 'Copy of '
    new_name = 'Copy of ' + action.name
    while Action.objects.filter(name=new_name,
                                workflow=workflow).exists():
        new_name = 'Copy of ' + new_name

    old_id = action.id
    old_name = action.name
    action = clone_action(action, new_workflow=None, new_name=new_name)

    # Log event
    Log.objects.register(request.user,
                         Log.ACTION_CLONE,
                         workflow,
                         {'id_old': old_id,
                          'id_new': action.id,
                          'name_old': old_name,
                          'name_new': action.name})
    data['form_is_valid'] = True
    data['html_redirect'] = reverse('action:index')

    messages.success(request,
                     'Action successfully cloned.')

    return redirect(reverse('action:index'))


@login_required
def thanks(request):
    """
    A page simply saying thanks
    :param request:
    :return:
    """
    return render(request, 'thanks.html', {})
