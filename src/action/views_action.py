# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from collections import OrderedDict

try:
    import urlparse
    from urllib import urlencode
except:  # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode

import django_tables2 as tables
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, reverse, render
from django.template import Context, Template
from django.template.loader import render_to_string
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import logs.ops
from action.evaluate import evaluate_row
from dataops import ops, pandas_db
from django_auth_lti.decorators import lti_role_required
from ontask.permissions import UserIsInstructor, is_instructor
from workflow.ops import get_workflow
from .forms import (
    ActionForm,
    EditActionOutForm,
    EnableURLForm,
    EditActionInForm,
    EnterActionIn,
    field_prefix
)
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
                      'td': {'style': 'text-align:left;'}}
        self.orderable = False

    def render(self, record):
        return render_to_string(
            self.template_file,
            {'id': record.id,
             'is_out': int(record.is_out),
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

    is_out = tables.Column(
        attrs={'td': {'class': 'dt-body-center'}},
        verbose_name=str('Type')

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

    def render_is_out(self, record):
        if record.is_out:
            return "OUT"
        else:
            return "IN"

    class Meta:
        model = Action

        fields = ('name', 'description_text', 'is_out', 'modified')

        sequence = ('name', 'description_text', 'is_out', 'modified')

        exclude = ('n_selected_rows', 'content', 'serve_enabled',
                   'columns', 'filter')

        attrs = {
            'class': 'table display table-bordered',
            'id': 'item-table'
        }

        row_attrs = {
            'style': 'text-align:center;',
            'class': lambda record: 'success' if record.is_out else ''
        }


def save_action_form(request, form, is_out, template_name):
    """
    Function to process JSON POST requests when creating a new action. It
    simply processes name and description and sets the other fields in the
    record.
    :param request: Request object
    :param form: Form to be used in the request/render
    :param is_out: Boolean stating if the formula is of type out or in
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

            # Type of action
            action_item.is_out = is_out

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
            logs.ops.put(request.user,
                         'action_create' if is_new else 'action_update',
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
                if is_out:
                    data['html_redirect'] = reverse(
                        'action:edit_out', kwargs={'pk': action_item.id}
                    )
                else:
                    data['html_redirect'] = reverse(
                        'action:edit_in', kwargs={'pk': action_item.id}
                    )
            else:
                data['html_redirect'] = reverse('action:index')

            # Enough said. Respond.
            return JsonResponse(data)

    data['html_form'] = render_to_string(template_name,
                                         {'form': form,
                                          'is_out': int(is_out)},
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

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return save_action_form(request,
                                form,
                                self.kwargs['type'] == '1',
                                self.template_name)

    def post(self, request, type):
        form = self.form_class(request.POST)
        return save_action_form(request,
                                form,
                                self.kwargs['type'] == '1',
                                self.template_name)


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

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=Action.objects.get(pk=kwargs['pk']))
        return save_action_form(request,
                                form,
                                self.kwargs['type'] == '1',
                                self.template_name)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST,
                               instance=Action.objects.get(pk=kwargs['pk']))
        return save_action_form(request,
                                form,
                                self.kwargs['type'] == '1',
                                self.template_name)


@user_passes_test(is_instructor)
def edit_action_out(request, pk):
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
    form = EditActionOutForm(request.POST or None, instance=action)

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
                return render(request, 'action/edit_out.html', context)

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
    return render(request, 'action/edit_out.html', context=context)


@user_passes_test(is_instructor)
def edit_action_in(request, pk):
    """
    View to handle the AJAX form to edit an action in (filter + columns).
    :param request: Request object
    :param pk: Action PK
    :return: JSON response
    """
    # Check if the workflow is locked
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    if workflow.nrows == 0:
        messages.error(request,
                       'Workflow has no data. '
                       'Go to Dataops to upload data.')
        return redirect(reverse('action:index'))

    # Get the action
    try:
        action = Action.objects.filter(
            Q(workflow__user=request.user) |
            Q(workflow__shared=request.user)).distinct().get(pk=pk)
    except ObjectDoesNotExist:
        return redirect('action:index')

    # Get the list of all columns from the workflow
    all_columns = workflow.columns.all()
    selected_columns = [c in action.columns.all()
                        for c in all_columns]

    # Create the form
    form = EditActionInForm(request.POST or None,
                            columns=workflow.columns.all(),
                            selected=selected_columns,
                            instance=action)

    # Create the context info. Col info is to render the table and contains
    # pairs of (form field, column object)
    select_col_fields = [f for f in form
                         if f.name.startswith(field_prefix)]
    ctx = {'col_info': zip(select_col_fields, all_columns),
           'action': action,
           'query_builder_ops': workflow.get_query_builder_ops_as_str(),
           'form': form, }

    # If it is a GET, or an invalid POST, render the template again
    if request.method == 'GET' or not form.is_valid():
        return render(request, 'action/edit_in.html', ctx)

    # Valid POST request

    # There must be at least a key and a non-key columns
    is_there_key = False
    is_there_nonkey = False
    for idx, c in enumerate(all_columns):
        # Check for the two conditions
        if c.is_key and form.cleaned_data[field_prefix + '%s' % idx]:
            is_there_key = True
        if not c.is_key and form.cleaned_data[field_prefix + '%s' % idx]:
            is_there_nonkey = True

    # Step 1: Make sure there is at least a unique column
    if not is_there_key:
        form.add_error(
            None,
            'There must be at least one unique column in the view'
        )
        ctx['form'] = form
        return render(request, 'action/edit_in.html', ctx)

    # Step 2: There must be at least on key column
    if not is_there_nonkey:
        form.add_error(
            None,
            'There must be at least one non-unique column in the view'
        )
        ctx['form'] = form
        return render(request, 'action/edit_in.html', ctx)

    # Save the element and populate the right columns
    action = form.save(commit=False)

    # Update set of columns (flush first)
    action.columns.clear()
    for idx, c in enumerate(all_columns):
        if not form.cleaned_data[field_prefix + '%s' % idx]:
            # Skip the columns that have not been selected
            continue
        action.columns.add(c)
    action.save()

    # Finish processing
    return redirect(reverse('action:index'))


def preview_response(request, pk, idx, template, prelude=None):
    """
    HTML request and the primary key of an action to preview one of its
    instances. The request must provide and additional parameter idx to
    denote which instance to show.

    :param request: HTML request object
    :param pk: Primary key of the an action for which to do the preview
    :param idx: Index of the reponse to preview
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
def run(request, pk):
    """
    Function that runs the action in. Mainly, it renders a table with
    all rows that satisfy the filter condition and includes a link to
    enter data for each of them.

    :param request:
    :param pk: Action id. It is assumed to be an action In
    :return:
    """

    # Get the workflow first
    workflow = get_workflow(request)
    if not workflow:
        return redirect('workflow:index')

    if workflow.nrows == 0:
        messages.error(request,
                       'Workflow has no data. '
                       'Go to Dataops to upload data.')
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

    return render(request,
                  'action/run.html',
                  {'columns': action.columns.all(),
                   'action': action})


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
def run_ss(request, pk):
    """
    Serve the AJAX requests to show the elements in the table that satisfy
    the filter and between the given limits.
    :param request:
    :param pk: action id being run
    :return:
    """

    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse({'error': 'Incorrect request. Unable to process'})

    # If there is not DF, go to workflow details.
    if not ops.workflow_id_has_table(workflow.id):
        return JsonResponse({'error': 'There is no data in the table'})

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
        return JsonResponse({'error': 'Incorrect request. Unable to process'})

    # Get the column information from the request and the rest of values.
    search_value = request.POST.get('search[value]', None)

    # Get columns
    columns = action.columns.all()
    column_names = [x.name for x in columns]

    # See if an order column has been given.
    if order_col:
        order_col = columns[int(order_col)]

    # Find the first key column
    key_name = column_names[0]
    key_idx = 0

    # Get the search pairs of field, value
    cv_tuples = []
    if search_value:
        cv_tuples = [(c.name, search_value, c.data_type) for c in columns]

    # Get the query set (including the filter in the action)
    qs = pandas_db.search_table_rows(
        workflow.id,
        cv_tuples,
        True,
        order_col,
        order_dir == 'asc',
        [cn for cn in column_names],  # Column names in the action
        action.filter  # Filter in the action
    )[start:]

    # Post processing + adding operations
    final_qs = []
    items = 0
    for row in qs:
        items += 1

        # Render the first element (the key) as the link to the page to update
        # the content.
        dst_url = reverse('action:run_row', kwargs={'pk': action.id})
        url_parts = list(urlparse.urlparse(dst_url))
        query = dict(urlparse.parse_qs(url_parts[4]))
        query.update({'uatn': column_names[0], 'uatv': row[0]})
        url_parts[4] = urlencode(query)
        link_item = '<a href="{0}">{1}</a>'.format(
            urlparse.urlunparse(url_parts), row[0]
        )

        # Add the row for rendering
        final_qs.append(OrderedDict(zip(column_names,
                                        [link_item] + list(row)[1:])))

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
def run_row(request, pk):
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
        messages.error(request,
                       'Workflow has no data. '
                       'Go to Dataops to upload data.')
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


def serve_action_in(request, action, user_attribute_name, is_inst):
    """
    Function that given a request, and an action IN, it performs the lookup
     and data input of values.
    :param request: HTTP request
    :param action:  Action In
    :param user_attribute_name: The column name used to check for email
    :param is_inst: Boolean stating if the user is instructor
    :return:
    """

    # Get the attribute value
    if is_inst:
        user_attribute_value = request.GET.get('uatv', None)
    else:
        user_attribute_value = request.user.email

    # Get the columns attached to the action
    columns = action.columns.all()

    # Get the row values. User_instance has the record used for verification
    row_pairs = pandas_db.get_table_row_by_key(
        action.workflow,
        None,
        (user_attribute_name, user_attribute_value),
        [c.name for c in columns]
    )

    # If the data has not been found, flag
    if not row_pairs:
        if not is_inst:
            return render(request, '404.html', {})

        messages.error(request,
                       'Data not found in the table')
        return redirect(reverse('action:run', kwargs={'pk': action.id }))

    # Bind the form with the existing data
    form = EnterActionIn(request.POST or None,
                         columns=columns,
                         values=row_pairs.values())
    # Create the context
    context = {'form': form, 'action': action}

    if request.method == 'GET' or not form.is_valid():
        return render(request, 'action/run_row.html', context)

    # Correct POST request!
    if not form.has_changed():
        if not is_inst:
            return render(request, 'thanks.html', {})

        return redirect(reverse('action:run', kwargs={'pk': action.id}))

    # Post with different data. # Update content in the DB
    set_fields = []
    set_values = []
    where_field = None
    where_value = None
    log_payload = []
    # Create the SET name = value part of the query
    for idx, column in enumerate(columns):
        value = form.cleaned_data[field_prefix + '%s' % idx]
        if column.is_key:
            if not where_field:
                # Remember one unique key for selecting the row
                where_field = column.name
                where_value = value
            continue

        set_fields.append(column.name)
        set_values.append(value)
        log_payload.append((column.name, value))

    pandas_db.update_row(action.workflow.id,
                         set_fields,
                         set_values,
                         [where_field],
                         [where_value])

    # Log the event
    logs.ops.put(request.user,
                 'tablerow_update',
                 action.workflow,
                 {'id': action.workflow.id,
                  'name': action.workflow.name,
                  'new_values': log_payload})

    # If not instructor, just thank the user!
    if not is_inst:
        return render(request, 'thanks.html', {})

    # Back to running the action
    return redirect(reverse('action:run', kwargs={'pk': action.id}))


def serve_action_out(user, action, user_attribute_name):
    """
    Function that given a user and an Action Out
    searches for the appropriate data in the table with the given
    attribute name equal to the user email and returns the HTTP response.
    :param user: User object making the request
    :param action: Action to execute (action out)
    :param user_attribute_name: Column to check for email
    :return:
    """
    # User_instance has the record used for verification
    action_content = evaluate_row(action, (user_attribute_name,
                                           user.email))

    # If the action content is empty, forget about it
    if action_content is None:
        raise Http404

    # Log the event
    logs.ops.put(
        user,
        'action_served_execute',
        workflow=action.workflow,
        payload={'action': action.name,
                 'action_id': action.id}
    )

    # Respond the whole thing
    return HttpResponse(action_content)


