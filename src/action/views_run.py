# -*- coding: utf-8 -*-

"""Views to run actions."""
import random
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from action.evaluate_action import (
    action_condition_evaluation, action_evaluation_context, get_row_values,
)
from action.form_edit import EnterActionIn
from action.forms import field_prefix
from action.forms_run import ValueExcludeForm
from action.models import Action
from action.ops import get_workflow_action, serve_action_out
from action.views_out import (
    run_canvas_email_action, run_email_action, run_json_action,
)
from dataops import pandas_db
from logs.models import Log
from ontask import get_action_payload
from ontask.permissions import is_instructor
from ontask.views import ontask_handler404
from workflow.ops import get_workflow


@csrf_exempt
@xframe_options_exempt
@login_required
def serve(request: HttpRequest, action_id: int) -> HttpResponse:
    """Serve the rendering of an action in a workflow for a given user.

    - uatn: User attribute name. The attribute to check for authentication.
      By default this will be "email".

    - uatv: User attribute value. The value to check with respect to the
      previous attribute. The default is the user attached to the request.

    If the two last parameters are given, the authentication is done as:

    user_record[user_attribute_name] == user_attribute_value

    :param request: Http Request
    :param action_id: Action ID to use
    :return: Http response
    """
    # Get the param dicts
    if request.method == 'POST':
        request_params = request.POST
    else:
        request_params = request.GET

    # Get the parameters
    user_attribute_name = request_params.get('uatn', 'email')

    # Get the action object
    action = Action.objects.filter(pk=int(action_id)).prefetch_related(
        'conditions',
    ).first()
    if not action:
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
def run(request: HttpRequest, pk: int) -> HttpResponse:
    """Run specific run action view depending on action type.

    If it is a Survey or todo, renders a table with all rows that
    satisfy the filter condition and includes a link to enter data for each
    of them.

    :param request: HttpRequest
    :param pk: Action id. It is assumed to be an action In
    :return: HttpResponse
    """
    # Get the workflow and action
    workflow, action = get_workflow_action(request, pk)

    # If nothing found, return
    if not workflow:
        return redirect(reverse('action:index'))

    if action.action_type == Action.personalized_text:
        return run_email_action(request, workflow, action)

    if action.action_type == Action.survey \
        or action.action_type == Action.todo_list:
        # Render template with active columns.
        response = render(
            request,
            'action/run_survey.html',
            {
                'columns': [
                    cc_pair.column
                    for cc_pair in action.column_condition_pair.all()
                    if cc_pair.column.is_active],
                'action': action,
            },
        )

    elif action.action_type == Action.personalized_canvas_email:
        response = run_canvas_email_action(request, workflow, action)

    elif action.action_type == Action.personalized_json:
        response = run_json_action(request, workflow, action)
    else:
        # Incorrect type of action.
        response = redirect(reverse('action:index'))

    return response


@user_passes_test(is_instructor)
@csrf_exempt
@require_http_methods(['POST'])
def run_survey_ss(request: HttpRequest, pk: int) -> JsonResponse:
    """Show elements in table that satisfy filter request.

    Serve the AJAX requests to show the elements in the table that satisfy
    the filter and between the given limits.
    :param request:
    :param pk: action id being run
    :return:
    """
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return JsonResponse(
            {'error': _('Incorrect request. Unable to process')},
        )

    # If there is not DF, go to workflow details.
    if not workflow.has_table():
        return JsonResponse({'error': _('There is no data in the table')})

    # Get the action
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not action:
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
            {'error': _('Incorrect request. Unable to process')},
        )

    # Get the column information from the request and the rest of values.
    search_value = request.POST.get('search[value]', None)

    # Get columns and the position of the first key
    columns = [ccpair.column for ccpair in action.column_condition_pair.all()]
    column_names = [col.name for col in columns]
    key_idx = next(idx for idx, col in enumerate(columns) if col.is_key)

    # See if an order column has been given.
    if order_col:
        order_col = columns[int(order_col)]

    # Get the search pairs of field, value
    cv_tuples = []
    if search_value:
        cv_tuples = [
            (col.name, search_value, col.data_type) for col in columns]

    # Get the query set (including the filter in the action)
    qs = pandas_db.search_table_rows(
        workflow.get_data_frame_table_name(),
        cv_tuples,
        True,
        order_col.name,
        order_dir == 'asc',
        column_names,  # Column names in the action
        action.get_filter_formula(),
    )

    # Post processing + adding operations
    final_qs = []
    item_count = 0
    for row in qs[start:start + length]:
        item_count += 1

        # Render the first element (the key) as the link to the page to update
        # the content.
        dst_url = reverse('action:run_survey_row', kwargs={'pk': action.id})
        url_parts = list(urlparse(dst_url))
        query = dict(parse_qs(url_parts[4]))
        query.update({'uatn': column_names[key_idx], 'uatv': row[key_idx]})
        url_parts[4] = urlencode(query)
        link_item = '<a href="{0}">{1}</a>'.format(
            urlunparse(url_parts), row[key_idx],
        )
        row = list(row)
        row[key_idx] = link_item

        # Add the row for rendering
        final_qs.append(row)

        if item_count == length:
            # We reached the number or requested elements, abandon loop
            break

    return JsonResponse({
        'draw': draw,
        'recordsTotal': workflow.nrows,
        'recordsFiltered': len(qs),
        'data': final_qs,
    })


@user_passes_test(is_instructor)
def run_survey_row(request: HttpRequest, pk: int) -> HttpResponse:
    """Render form for introducing information in a single row.

    Function that runs the action in for a single row. The request
    must have query parameters uatn = key name and uatv = key value to
    perform the lookup.

    :param request:
    :param pk: Action id. It is assumed to be an action In
    :return:
    """
    # Get the workflow first
    workflow = get_workflow(request, prefetch_related='actions')
    if not workflow:
        return redirect('home')

    if workflow.nrows == 0:
        messages.error(
            request,
            _('Workflow has no data. '
              + 'Go to "Manage table data" to upload data.'),
        )
        return redirect(reverse('action:index'))

    # Get the action
    action = workflow.actions.filter(
        pk=pk,
    ).filter(
        Q(workflow__user=request.user) | Q(workflow__shared=request.user),
    ).first()
    if not action:
        return redirect('action:index')

    # If the action is an "out" action, return to index
    if action.is_out:
        return redirect('action:index')

    # Get the parameters
    user_attribute_name = request.GET.get('uatn', 'email')

    return serve_action_in(request, action, user_attribute_name, True)


def serve_action_in(
    request: HttpRequest,
    action: Action,
    user_attribute_name: str,
    is_inst: bool,
) -> HttpResponse:
    """Serve a request for action in.

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

    # Get the active columns attached to the action
    colcon_items = [
        pair for pair in action.column_condition_pair.all()
        if pair.column.is_active
    ]

    if action.shuffle:
        # Shuffle the columns if needed
        random.seed(request.user)
        random.shuffle(colcon_items)

    # Get the row values. User_instance has the record used for verification
    # User_instance has the record used for verification
    row_values = get_row_values(
        action,
        (user_attribute_name, user_attribute_value))
    # Obtain the dictionary with the condition evaluation
    condition_evaluation = action_condition_evaluation(action, row_values)
    # Get the dictionary containing column names, attributes and condition
    # valuations:
    context = action_evaluation_context(
        action,
        row_values,
        condition_evaluation)

    if not row_values:
        # If the data has not been found, flag
        if not is_inst:
            return ontask_handler404(request, None)

        messages.error(
            request,
            _('Data not found in the table'))
        return redirect(reverse('action:run', kwargs={'pk': action.id}))

    # Bind the form with the existing data
    form = EnterActionIn(
        request.POST or None,
        tuples=colcon_items,
        context=context,
        values=[context[colcon.column.name] for colcon in colcon_items],
        show_key=is_inst)

    cancel_url = None
    if is_inst:
        cancel_url = reverse('action:run', kwargs={'pk': action.id})

    no_process = (
        request.method == 'GET'
        or not form.is_valid()
        or request.POST.get('lti_version', None))
    if no_process:
        return render(
            request,
            'action/run_survey_row.html',
            {'form': form,
             'action': action,
             'cancel_url': cancel_url})

    # Post with different data. # Update content in the DB
    set_fields = []
    set_values = []
    where_field = 'email'
    where_value = request.user.email
    log_payload = []
    # Create the SET name = value part of the query
    for idx, colcon in enumerate(colcon_items):
        if not is_inst and colcon.column.is_key:
            # If it is a learner request and a key column, skip
            continue

        # Skip the element if there is a condition and it is false
        if colcon.condition and not context[colcon.condition.name]:
            continue

        field_value = form.cleaned_data[field_prefix + '{0}'.format(idx)]
        if colcon.column.is_key:
            # Remember one unique key for selecting the row
            where_field = colcon.column.name
            where_value = field_value
            continue

        set_fields.append(colcon.column.name)
        set_values.append(field_value)
        log_payload.append((colcon.column.name, field_value))

    pandas_db.update_row(
        action.workflow.get_data_frame_table_name(),
        set_fields,
        set_values,
        [where_field],
        [where_value])

    # Recompute all the values of the conditions in each of the actions
    for act in action.workflow.actions.all():
        act.update_n_rows_selected()

    # Log the event and update its content in the action
    log_item = Log.objects.register(
        request.user,
        Log.TABLEROW_UPDATE,
        action.workflow,
        {'id': action.workflow.id,
         'name': action.workflow.name,
         'new_values': log_payload})

    # Modify the time of execution for the action
    action.last_executed_log = log_item
    action.save()

    # If not instructor, just thank the user!
    if not is_inst:
        return render(request, 'thanks.html', {})

    # Back to running the action
    return redirect(reverse('action:run', kwargs={'pk': action.id}))


@user_passes_test(is_instructor)
def run_action_item_filter(request: HttpRequest) -> HttpResponse:
    """Offer a select widget to tick students to exclude from the email.

    :param request: HTTP request (GET)
    :return: HTTP response
    """
    # Get the payload from the session, and if not, use the given one
    payload = get_action_payload(request)
    if not payload:
        # Something is wrong with this execution. Return to the action table.
        messages.error(request, _('Incorrect item filter invocation.'))
        return redirect('action:index')

    # Get the information from the payload
    action = Action.objects.get(pk=payload['action_id'])

    form = ValueExcludeForm(
        request.POST or None,
        action=action,
        column_name=payload['item_column'],
        exclude_values=payload.get('exclude_values', list),
    )
    context = {
        'form': form,
        'action': action,
        'button_label': payload['button_label'],
        'valuerange': range(payload.get('valuerange', 0)),
        'step': payload.get('step', 0),
        'prev_step': payload['prev_url'],
    }

    # Process the initial loading of the form and return
    if request.method != 'POST' or not form.is_valid():
        return render(request, 'action/item_filter.html', context)

    # Updating the content of the exclude_values in the payload
    payload['exclude_values'] = form.cleaned_data['exclude_values']

    return redirect(payload['post_url'])
