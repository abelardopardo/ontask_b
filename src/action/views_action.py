# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import django_tables2 as tables
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, reverse, render
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt

import logs.ops
from action.evaluate import evaluate_row
from dataops import ops
from django_auth_lti.decorators import lti_role_required
from ontask.permissions import is_instructor, UserIsInstructor
from workflow.ops import get_workflow
from .forms import ActionForm, EditActionForm, EnableURLForm
from .models import Action, Condition


#
# Classes for Table rendering
#

class OperationsColumn(tables.Column):
    """
    This class is to render a column in which various buttons are shown for
     different operations (open, rename, export, URL, send emails, etc)
    """

    empty_values = []

    def __init__(self, *args, **kwargs):
        self.template_file = kwargs.pop('template_file')
        super(OperationsColumn, self).__init__(*args, **kwargs)
        self.attrs = {'th': {'style': 'text-align:center;'},
                      'td': {'style': 'text-align:center;'}}
        self.orderable = False

    def render(self, record):
        return render_to_string(
            self.template_file,
            {'id': record.id,
             'serve_enabled': record.serve_enabled})


class ActionTable(tables.Table):
    """
    Table to render the list of actions per workflow. The Operations column is
     taken from another class to centralise the customisation.
    """

    name = tables.Column(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=str('Name')
    )

    description_text = tables.Column(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=str('Description')
    )

    modified = tables.DateTimeColumn(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name='Modified'

    )

    operations = OperationsColumn(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name='Operations',
        template_file='action/includes/partial_action_operations.html',
        orderable=False
    )

    def __init__(self, data, *args, **kwargs):
        super(ActionTable, self).__init__(data, *args, **kwargs)

    def render_name(self, record):
        return format_html(
            """<a href="{0}">{1}</a>""".format(
                reverse('action:edit', kwargs={'pk': record.id}),
                record.name
            )
        )

    class Meta:
        model = Action

        fields = ('name', 'description_text', 'modified')

        sequence = ('name', 'description_text', 'modified')

        exclude = ('n_selected_rows', 'content', 'serve_enabled')

        attrs = {
            'class': 'table display table-bordered',
            'id': 'item-table'
        }

        row_attrs = {
            'style': 'text-align:center;'
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

    # JSON payload
    data = dict()

    # By default, we assume that the POST is not correct.
    data['form_is_valid'] = False

    # Process the POST
    if request.method == 'POST':
        if form.is_valid():
            # Partial validity. Additional checks

            # Fill in the fields of the action (without saving to DB)_
            action_item = form.save(commit=False)

            # Is this a new action?
            is_new = action_item.pk is None

            # Get the corresponding workflow
            workflow = get_workflow(request)
            if not workflow:
                redirect('workflow:index')

            # Verify that that action does comply with the name uniqueness
            # property (only with respec to other actions)
            if is_new:  # Action is New
                if Action.objects.filter(workflow=workflow,
                                         workflow__user=request.user,
                                         name=action_item.name).exists():
                    # There is an action with this name already
                    form.add_error('name',
                                   'An action with that name already exists')
                    data['html_redirect'] = reverse('action:index')
                else:
                    # Correct New action. Proceed with the
                    action_item.user = request.user
                    action_item.workflow = workflow
                    action_item.n_selected_rows = -1

            # Save item in the DB now
            action_item.save()

            # Log the event
            if is_new:
                # Action creation event
                logs.ops.put(request.user,
                             'action_create',
                             action_item.workflow,
                             {'id': action_item.id,
                              'name': action_item.name,
                              'workflow_id': workflow.id,
                              'workflow_name': workflow.name})
            else:
                # Action update event
                logs.ops.put(request.user,
                             'action_update',
                             action_item.workflow,
                             {'id': action_item.id,
                              'name': action_item.name,
                              'workflow_id': workflow.id,
                              'workflow_name': workflow.name})

            # Request is correct
            data['form_is_valid'] = True
            if is_new:
                # If a new action is created, jump to the action edit page.
                # This could be changed to go back to the action:index
                data['html_redirect'] = reverse(
                    'action:edit', kwargs={'pk': action_item.id}
                )
            else:
                data['html_redirect'] = reverse('action:index')

            # Enough said. Respond.
            return JsonResponse(data)

    data['html_form'] = render_to_string(template_name,
                                         {'form': form},
                                         request=request)
    return JsonResponse(data)


def preview_response(request, pk, idx, template, prelude=None):
    """
    HTML request and the primary key of an action to preview one of its
    instances. The request must provide and additional parameter idx to
    denote which instance to show.

    :param request: HTML request object
    :param pk: Primary key of the an action for which to do the preview
    :param template: Path to the template to use for the render.
    :param prelude: Optional text to include at the top of the rencering
    :return:
    """

    # To include in the JSON response
    data = dict()

    # Action being used
    try:
        action = Action.objects.get(id=pk)
    except ObjectDoesNotExist:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    # Get the workflow to obtain row numbers
    workflow = get_workflow(request, action.workflow.id)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    # If the request has the 'action_content' field, update the action
    action_content = request.GET.get('action_content', None)
    if action_content:
        action.content = action_content
        action.save()

    # Turn the parameter into an integer
    idx = int(idx)

    # Get the total number of items
    n_items = action.n_selected_rows
    if n_items == -1:
        n_items = workflow.nrows

    # Set the idx to a legal value just in case
    if not 1 <= idx <= n_items:
        idx = 1

    prv = idx - 1
    if prv <= 0:
        prv = n_items

    nxt = idx + 1
    if nxt > n_items:
        nxt = 1

    action_content = evaluate_row(action, idx)
    if action_content is None:
        action_content = \
            "Error while retrieving content for row {0}".format(idx)

    data['html_form'] = \
        render_to_string(template,
                         {'action': action,
                          'action_content': action_content,
                          'index': idx,
                          'nxt': nxt,
                          'prv': prv,
                          'prelude': prelude},
                         request=request)

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

    # Get the actions
    actions = Action.objects.filter(workflow__id=workflow.id)

    # Context to render the template
    context = {}

    # Build the table only if there is anything to show (prevent empty table)
    if len(actions) > 0:
        context['table'] = ActionTable(actions, orderable=False)

    return render(request, 'action/index.html', context)


class ActionCreateView(UserIsInstructor, generic.TemplateView):
    """
    CBV to handle the create action form (very simple)
    """
    form_class = ActionForm
    template_name = 'action/includes/partial_action_create.html'

    def get_context_data(self, **kwargs):
        context = super(ActionCreateView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return save_action_form(request, form, self.template_name)

    def post(self, request):
        form = self.form_class(request.POST)
        return save_action_form(request, form, self.template_name)


class ActionUpdateView(UserIsInstructor, generic.DetailView):
    """
    CBV to handle the update (as in name and description) action.
    @DynamicAttrs
    """
    model = Action
    template_name = 'action/includes/partial_action_update.html'
    context_object_name = 'action'
    form_class = ActionForm

    def get_object(self, queryset=None):
        obj = super(ActionUpdateView, self).get_object(queryset=queryset)
        if obj.workflow.id != self.request.session['ontask_workflow_id']:
            raise Http404()

        return obj

    def get_context_data(self, **kwargs):
        context = super(ActionUpdateView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=Action.objects.get(pk=kwargs['pk']))
        return save_action_form(request, form, self.template_name)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST,
                               instance=Action.objects.get(pk=kwargs['pk']))
        return save_action_form(request, form, self.template_name)


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
        logs.ops.put(request.user,
                     'action_delete',
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
def edit_action(request, pk):
    """
    View to handle the AJAX form to edit an action (editor, conditions,
    filters, etc).
    :param request: Request object
    :param pk: Action PK
    :return: JSON response
    """

    # Try to get the workflow first
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    # Get the action and create the form
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)).distinct().get(pk=pk)
    except ObjectDoesNotExist:
        return redirect('action:index')

    # Create the form
    form = EditActionForm(request.POST or None, instance=action)

    # See if the action has a filter or not
    try:
        filter_condition = Condition.objects.get(action=action, is_filter=True)
    except Condition.DoesNotExist:
        filter_condition = None
    except Condition.MultipleObjectsReturned:
        return render(request, 'error.html',
                      {'message': 'Malfunction detected when retrieving filter '
                                  '(action: {0})'.format(action.id)})

    # Conditions to show in the page as well.
    conditions = Condition.objects.filter(
        action=action, is_filter=False).order_by('created')

    # Boolean to find out if there is a table attached to this workflow
    has_data = ops.workflow_has_table(action.workflow)

    # Get the total number of rows in DF and those selected by filter.
    total_rows = workflow.nrows
    selected_rows = action.n_selected_rows

    # Context to render the form
    context = {'filter_condition': filter_condition,
               'action': action,
               'conditions': conditions,
               'query_builder_ops': workflow.get_query_builder_ops_as_str(),
               'attribute_names': [x for x in workflow.attributes.keys()],
               'column_names': workflow.get_column_names(),
               'selected_rows': selected_rows,
               'has_data': has_data,
               'total_rows': total_rows,
               'form': form}

    # Processing the request after receiving the text from the editor
    if request.method == 'POST':
        # Get the next step
        next_step = request.POST['Submit']

        if form.is_valid():
            content = form.cleaned_data.get('content', None)
            # TODO: Can we detect unused vars only for this invocation?
            # Render the content as a template and catch potential problems.
            # This seems to be only possible if dealing directly with Jinja2
            # instead of Django.
            try:
                Template(content).render(Context({}))
            except Exception as e:
                # Pass the django exception to the form (fingers crossed)
                form.add_error(None, e.message)
                return render(request, 'action/edit.html', context)

            # Log the event
            logs.ops.put(request.user,
                         'action_update',
                         action.workflow,
                         {'id': action.id,
                          'name': action.name,
                          'workflow_id': workflow.id,
                          'workflow_name': workflow.name,
                          'content': content})

            # Text is good. Update the content of the action
            action.content = content
            action.save()

            # Closing
            if next_step == 'Save-and-close':
                return redirect('action:index')

    # Return the same form in the same page
    return render(request, 'action/edit.html', context=context)


@user_passes_test(is_instructor)
def preview(request, pk, idx):
    """
    HTML request and the primary key of an action to preview one of its
    instances. The request must provide and additional parameter idx to
    denote which instance to show.

    :param request: HTML request object
    :param pk: Primary key of the an action for which to do the preview
    :param idx: Index of the element to preview (from the queryset)
    :return:
    """

    return preview_response(request,
                            pk,
                            idx,
                            'action/includes/partial_action_preview.html')


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
    data = {}

    # Get the action object
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)).distinct().get(pk=pk)
    except Action.DoesNotExist:
        return redirect(reverse('workflow:index'))

    form = EnableURLForm(request.POST or None, instance=action)

    if request.method == 'POST' and form.is_valid():
        if form.has_changed():
            # Reflect the change in the action element
            form.save()

            # Recording the event
            logs.ops.put(
                request.user,
                'action_serve_toggled',
                action.workflow,
                {'id': action.id,
                 'name': action.name,
                 'serve_enabled': action.serve_enabled})

        return redirect(reverse('action:index'))

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
@lti_role_required(['Instructor', 'Student'])
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

    # If the id is not numeric, return 404
    if not action_id.isnumeric():
        raise Http404

    # Get the action object
    try:
        action = Action.objects.get(pk=int(action_id))
    except ObjectDoesNotExist:
        raise Http404

    # If it is not enabled, reject the request
    if not action.serve_enabled:
        raise Http404

    # Successful request. User_instance has the record used for verification
    action_content = evaluate_row(action, (user_attribute_name,
                                           request.user.email))

    # If the action content is empty, forget about it
    if action_content is None:
        raise Http404

    # Log the event
    logs.ops.put(
        request.user,
        'action_served_execute',
        workflow=action.workflow,
        payload={'action': action.name,
                 'action_id': action.id}
    )

    # Respond the whole thing
    return HttpResponse(action_content)
