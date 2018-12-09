# -*- coding: utf-8 -*-


from builtins import range
import random

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from action.models import Condition, Action
from dataops import ops, formula_evaluation, pandas_db
from logs.models import Log
from ontask.permissions import is_instructor
from .forms import (ColumnRenameForm,
                    ColumnAddForm,
                    FormulaColumnAddForm,
                    RandomColumnAddForm, QuestionAddForm, QuestionRenameForm)
from .models import Column
from .ops import (
    get_workflow,
    workflow_delete_column,
    clone_column,
    reposition_column_and_update_df, workflow_restrict_column)

# These are the column operands offered through the GUI. They have immediate
# translations onto Pandas operators over dataframes.
# Each tuple has:
# - Pandas operation name
# - Textual description
# - List of data types that are allowed (for data type checking)
formula_column_operands = [
    ('sum', _('sum: Sum selected columns'), ['integer', 'double']),
    ('prod', _('prod: Product of the selected columns'), ['integer', 'double']),
    ('max', _('max: Maximum of the selected columns'), ['integer', 'double']),
    ('min', _('min: Minimum of the selected columns'), ['integer', 'double']),
    ('mean', _('mean: Mean of the selected columns'), ['integer', 'double']),
    ('median', _('median: Median of the selected columns'),
     ['integer', 'double']),
    ('std', _('std: Standard deviation over the selected columns'),
     ['integer', 'double']),
    ('all', _('all: True when all elements in selected columns are true'),
     ['boolean']),
    ('any', _('any: True when any element in selected columns is true'),
     ['boolean']),
]

def partition(list_in, n):
    """
    Given a list and n, returns a list with n lists, and inside each of them a
    set of elements from the shuffled list. All lists are of the same size
    :param list_in: List of elements to partition
    :param n: Number of partitions
    :return: List of lists with shuffled elements partitioned
    """
    random.shuffle(list_in)
    return [list_in[i::n] for i in range(n)]


@user_passes_test(is_instructor)
def column_add(request, pk=None):
    # Data to send as JSON response
    data = {}

    # Detect if this operation is to add a new column or a new question (in
    # the edit in page)
    is_question = pk is not None

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    if workflow.nrows == 0:
        data['form_is_valid'] = True
        data['html_redirect'] = ''
        if is_question:
            messages.error(
                request,
                _('Cannot add question to a workflow without data')
            )
        else:
            messages.error(
                request,
                _('Cannot add column to a workflow without data')
            )
        return JsonResponse(data)

    action_id = None
    if pk:
        # Get the action and the columns
        try:
            action = Action.objects.filter(
                Q(workflow__user=request.user) |
                Q(workflow__shared=request.user)
            ).distinct().get(pk=pk)
        except ObjectDoesNotExist:
            messages.error(
                request,
                _('Cannot find action to add question.')
            )
            return JsonResponse({'html_redirect': reverse('action:index')})
        action_id = action.id

    # Form to read/process data
    if is_question:
        form = QuestionAddForm(request.POST or None, workflow=workflow)
    else:
        form = ColumnAddForm(request.POST or None, workflow=workflow)

    # If a GET or incorrect request, render the form again
    if request.method == 'GET' or not form.is_valid():
        if is_question:
            template = 'workflow/includes/partial_question_addedit.html'
        else:
            template = 'workflow/includes/partial_column_addedit.html'

        data['html_form'] = render_to_string(template,
                                             {'form': form,
                                              'is_question': is_question,
                                              'action_id': action_id,
                                              'add': True},
                                             request=request)

        return JsonResponse(data)

    # Processing now a valid POST request
    # Access the updated information
    column_initial_value = form.initial_valid_value

    # Save the column object attached to the form
    column = form.save(commit=False)

    # Fill in the remaining fields in the column
    column.workflow = workflow
    column.is_key = False

    # Update the data frame, which must be stored in the form because
    # it was loaded when validating it.
    df = pandas_db.load_from_db(workflow.id)

    # Add the column with the initial value to the dataframe
    df = ops.data_frame_add_column(df, column, column_initial_value)

    # Update the column type with the value extracted from the data frame
    column.data_type = \
        pandas_db.pandas_datatype_names[df[column.name].dtype.name]

    # Update the positions of the appropriate columns
    workflow.reposition_columns(workflow.ncols + 1, column.position)

    column.save()

    # Store the df to DB
    ops.store_dataframe_in_db(df, workflow.id)

    # If the column is a question, add it to the action
    if is_question:
        action.columns.add(column)

    # Log the event
    if is_question:
        event_type = Log.QUESTION_ADD
    else:
        event_type = Log.COLUMN_ADD
    Log.objects.register(request.user,
                         event_type,
                         workflow,
                         {'id': workflow.id,
                          'name': workflow.name,
                          'column_name': column.name,
                          'column_type': column.data_type})

    data['form_is_valid'] = True
    data['html_redirect'] = ''
    return JsonResponse(data)


@user_passes_test(is_instructor)
def formula_column_add(request):
    # Data to send as JSON response, in principle, assume form is not valid
    data = {'form_is_valid': False}

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    if workflow.nrows == 0:
        data['form_is_valid'] = True
        data['html_redirect'] = ''
        messages.error(
            request,
            _('Cannot add column to a workflow without data')
        )
        return JsonResponse(data)

    # Form to read/process data
    form = FormulaColumnAddForm(
        data=request.POST or None,
        operands=formula_column_operands,
        columns=workflow.columns.all()
    )

    # If a GET or incorrect request, render the form again
    if request.method == 'GET' or not form.is_valid():
        data['html_form'] = render_to_string(
            'workflow/includes/partial_formula_column_add.html',
            {'form': form},
            request=request
        )

        return JsonResponse(data)

    # Processing now a valid POST request

    # Save the column object attached to the form and add additional fields
    column = form.save(commit=False)
    column.workflow = workflow
    column.is_key = False

    # Save the instance
    try:
        column = form.save()
        form.save_m2m()
    except IntegrityError:
        form.add_error('name', _('A column with that name already exists'))
        data['html_form'] = render_to_string(
            'workflow/includes/partial_formula_column_add.html',
            {'form': form},
            request=request
        )
        return JsonResponse(data)

    # Update the data frame
    df = pandas_db.load_from_db(workflow.id)

    try:
        # Add the column with the appropriate computation
        operation = form.cleaned_data['op_type']
        cnames = [c.name for c in form.selected_columns]
        if operation == 'sum':
            df[column.name] = df[cnames].sum(axis=1)
        elif operation == 'prod':
            df[column.name] = df[cnames].prod(axis=1)
        elif operation == 'max':
            df[column.name] = df[cnames].max(axis=1)
        elif operation == 'min':
            df[column.name] = df[cnames].min(axis=1)
        elif operation == 'mean':
            df[column.name] = df[cnames].mean(axis=1)
        elif operation == 'median':
            df[column.name] = df[cnames].median(axis=1)
        elif operation == 'std':
            df[column.name] = df[cnames].std(axis=1)
        elif operation == 'all':
            df[column.name] = df[cnames].all(axis=1)
        elif operation == 'any':
            df[column.name] = df[cnames].any(axis=1)
        else:
            raise Exception(
                _('Operand {0} not implemented').format(operation)
            )
    except Exception as e:
        # Something went wrong in pandas, we need to remove the column
        column.delete()

        # Notify in the form
        form.add_error(
            None,
            _('Unable to perform the requested operation ({0})').format(
                e.message
            )
        )
        data['html_form'] = render_to_string(
            'workflow/includes/partial_formula_column_add.html',
            {'form': form},
            request=request
        )
        return JsonResponse(data)

    # Populate the column type
    column.data_type = \
        pandas_db.pandas_datatype_names[df[column.name].dtype.name]

    # Update the positions of the appropriate columns
    workflow.reposition_columns(workflow.ncols + 1, column.position)

    column.save()

    # Store the df to DB
    ops.store_dataframe_in_db(df, workflow.id)

    # Log the event
    Log.objects.register(request.user,
                         Log.COLUMN_ADD_FORMULA,
                         workflow,
                         {'id': workflow.id,
                          'name': workflow.name,
                          'column_name': column.name,
                          'column_type': column.data_type})

    # The form has been successfully processed
    data['form_is_valid'] = True
    data['html_redirect'] = ''  # Refresh the page
    return JsonResponse(data)


@user_passes_test(is_instructor)
def random_column_add(request):
    """
    Function that creates a column with random values (Modal)
    :param request:
    :return:
    """
    # Data to send as JSON response, in principle, assume form is not valid
    data = {'form_is_valid': False}

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    if workflow.nrows == 0:
        data['form_is_valid'] = True
        data['html_redirect'] = ''
        messages.error(
            request,
            _('Cannot add column to a workflow without data')
        )
        return JsonResponse(data)

    # Form to read/process data
    form = RandomColumnAddForm(data=request.POST or None)

    # If a GET or incorrect request, render the form again
    if request.method == 'GET' or not form.is_valid():
        data['html_form'] = render_to_string(
            'workflow/includes/partial_random_column_add.html',
            {'form': form},
            request=request
        )

        return JsonResponse(data)

    # Processing now a valid POST request

    # Save the column object attached to the form and add additional fields
    column = form.save(commit=False)
    column.workflow = workflow
    column.is_key = False

    # Save the instance
    try:
        column = form.save()
        form.save_m2m()
    except IntegrityError:
        form.add_error('name', _('A column with that name already exists'))
        data['html_form'] = render_to_string(
            'workflow/includes/partial_random_column_add.html',
            {'form': form},
            request=request
        )
        return JsonResponse(data)

    # Update the data frame
    df = pandas_db.load_from_db(workflow.id)

    # Get the values and interpret its meaning
    values = form.cleaned_data['values']
    int_value = None
    # First, try to see if the field is a valid integer
    try:
        int_value = int(values)
    except ValueError:
        pass

    if int_value:
        # At this point the field is an integer
        if int_value <= 1:
            form.add_error('values',
                           _('The integer value has to be larger than 1'))
            data['html_form'] = render_to_string(
                'workflow/includes/partial_random_column_add.html',
                {'form': form},
                request=request
            )
            return JsonResponse(data)

        vals = [x + 1 for x in range(int_value)]
        # df[column.name] = [random.randint(1, int_value)
        #                    for __ in range(workflow.nrows)]
    else:
        # At this point the field is a string and the values are the comma
        # separated strings.
        vals = [x.strip() for x in values.strip().split(',') if x]
        if not vals:
            form.add_error('values',
                           _('The value has to be a comma-separated list'))
            data['html_form'] = render_to_string(
                'workflow/includes/partial_random_column_add.html',
                {'form': form},
                request=request
            )
            return JsonResponse(data)

        # df[column.name] = [random.choice(vals) for __ in range(workflow.nrows)]

    # Empty new column
    new_column = [None] * workflow.nrows
    # Create the random partitions
    partitions = partition([x for x in range(workflow.nrows)], len(vals))
    # Assign values to partitions
    for idx, indeces in enumerate(partitions):
        for x in indeces:
            new_column[x] = vals[idx]

    # Assign the new column to the data frame
    df[column.name] = new_column

    # Populate the column type
    column.data_type = \
        pandas_db.pandas_datatype_names[df[column.name].dtype.name]

    # Update the positions of the appropriate columns
    workflow.reposition_columns(workflow.ncols + 1, column.position)

    column.save()

    # Store the df to DB
    ops.store_dataframe_in_db(df, workflow.id)

    # Log the event
    Log.objects.register(request.user,
                         Log.COLUMN_ADD_RANDOM,
                         workflow,
                         {'id': workflow.id,
                          'name': workflow.name,
                          'column_name': column.name,
                          'column_type': column.data_type,
                          'value': values})

    # The form has been successfully processed
    data['form_is_valid'] = True
    data['html_redirect'] = ''  # Refresh the page
    return JsonResponse(data)


@user_passes_test(is_instructor)
def column_edit(request, pk):
    # Data to send as JSON response
    data = {}

    # Detect if this operation is to edit a new column or a new question (in
    # the edit in page)
    is_question = 'question_edit' in request.path_info

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    # Get the column object and make sure it belongs to the workflow
    try:
        column = Column.objects.get(pk=pk,
                                    workflow=workflow)
    except ObjectDoesNotExist:
        # Something went wrong, redirect to the workflow detail page
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail',
                                        kwargs={'pk': workflow.id})
        return JsonResponse(data)

    # Form to read/process data
    if is_question:
        form = QuestionRenameForm(request.POST or None,
                                  workflow=workflow,
                                  instance=column)
    else:
        form = ColumnRenameForm(request.POST or None,
                                workflow=workflow,
                                instance=column)

    old_name = column.name
    # Keep a copy of the previous position
    old_position = column.position
    context = {'form': form,
               'cname': old_name,
               'pk': pk}

    if request.method == 'GET' or not form.is_valid():
        if is_question:
            template = 'workflow/includes/partial_question_addedit.html'
        else:
            template = 'workflow/includes/partial_column_addedit.html'
        data['html_form'] = render_to_string(template,
                                             context,
                                             request=request)

        return JsonResponse(data)

    # Processing a POST request with valid data in the form

    # Process further only if any data changed.
    if form.changed_data:

        # Some field changed value, so save the result, but
        # no commit as we need to propagate the info to the df
        column = form.save(commit=False)

        # If there is a new name, rename the data frame columns
        if 'name' in form.changed_data:
            pandas_db.db_column_rename(workflow.pk, old_name, column.name)

        if 'position' in form.changed_data:
            # Update the positions of the appropriate columns
            workflow.reposition_columns(old_position, column.position)

        # Save the column information
        form.save()

        # Changes in column require rebuilding the query_builder_ops
        workflow.set_query_builder_ops()

        # Save the workflow
        workflow.save()

    data['form_is_valid'] = True
    data['html_redirect'] = ''

    # Log the event
    if is_question:
        event_type = Log.QUESTION_ADD
    else:
        event_type = Log.COLUMN_ADD
    Log.objects.register(request.user,
                         event_type,
                         workflow,
                         {'id': workflow.id,
                          'name': workflow.name,
                          'column_name': old_name,
                          'new_name': column.name})

    # Done processing the correct POST request
    return JsonResponse(data)


@user_passes_test(is_instructor)
def column_delete(request, pk):
    """
    Delete a column in the table attached to a workflow
    :param request: HTTP request
    :param pk: ID of the column to delete. The workflow element is taken
     from the session.
    :return: Render the delete column form
    """

    # JSON response, context and default values
    data = dict()  # JSON response

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    data['form_is_valid'] = False
    context = {'pk': pk}  # For rendering

    # Get the column
    try:
        column = Column.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        # The column is not there. Redirect to workflow detail
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail',
                                        kwargs={'pk': workflow.id})
        return JsonResponse(data)

    # If the columns is unique and it is the only one, we cannot allow
    # the operation
    unique_column = workflow.get_column_unique()
    if column.is_key and len([x for x in unique_column if x]) == 1:
        # This is the only key column
        messages.error(request, _('You cannot delete the only key column'))
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail',
                                        kwargs={'pk': workflow.id})
        return JsonResponse(data)

    # Get the name of the column to delete
    context['cname'] = column.name

    # Get the conditions/actions attached to this workflow
    cond_to_delete = [x for x in Condition.objects.filter(
        action__workflow=workflow)
                      if formula_evaluation.has_variable(x.formula,
                                                         column.name)]
    # Put it in the context because it is shown to the user before confirming
    # the deletion
    context['cond_to_delete'] = cond_to_delete

    if request.method == 'POST':
        # Proceed deleting the column
        workflow_delete_column(workflow, column, cond_to_delete)

        # Log the event
        Log.objects.register(request.user,
                             Log.COLUMN_DELETE,
                             workflow,
                             {'id': workflow.id,
                              'name': workflow.name,
                              'column_name': column.name})

        data['form_is_valid'] = True

        # There are various points of return
        from_url = request.META['HTTP_REFERER']
        if from_url.endswith(reverse('table:display')):
            data['html_redirect'] = reverse('table:display')
        else:
            data['html_redirect'] = reverse('workflow:detail',
                                            kwargs={'pk': workflow.id})
        return JsonResponse(data)

    data['html_form'] = render_to_string(
        'workflow/includes/partial_column_delete.html',
        context,
        request=request)

    return JsonResponse(data)


@user_passes_test(is_instructor)
def column_clone(request, pk):
    """
    Clone a column in the table attached to a workflow
    :param request: HTTP request
    :param pk: ID of the column to clone. The workflow element is taken
     from the session.
    :return: Render the clone column form
    """

    # JSON response, context and default values
    data = dict()  # JSON response

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    data['form_is_valid'] = False
    context = {'pk': pk}  # For rendering

    # Get the column
    try:
        column = Column.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        # The column is not there. Redirect to workflow detail
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail',
                                        kwargs={'pk': workflow.id})
        return JsonResponse(data)

    # Get the name of the column to clone
    context['cname'] = column.name

    if request.method == 'GET':
        data['html_form'] = render_to_string(
            'workflow/includes/partial_column_clone.html',
            context,
            request=request)

        return JsonResponse(data)

    # POST REQUEST

    # Get the new name appending as many times as needed the 'Copy of '
    old_name = column.name
    new_name = 'Copy_of_' + old_name
    while Column.objects.filter(name=new_name,
                                workflow=column.workflow).exists():
        new_name = 'Copy_of_' + new_name

    # Proceed to clone the column
    column = clone_column(column, None, new_name)

    # Log the event
    Log.objects.register(request.user,
                         Log.COLUMN_CLONE,
                         workflow,
                         {'id': workflow.id,
                          'name': workflow.name,
                          'old_column_name': old_name,
                          'new_column_name': column.name})

    data['form_is_valid'] = True
    data['html_redirect'] = ''

    return JsonResponse(data)


@user_passes_test(is_instructor)
def column_move_prev(request, pk):
    """

    :param request: HTTP request to move a column to its previous position
    :param pk: Column ID
    :return:
    """

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse({'html_redirect': reverse('workflow:index')})

    # Get the column
    try:
        column = Column.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        return JsonResponse({
            'html_redirect': reverse('workflow:detail',
                                     kwargs={'pk': workflow.id})
        })

    # The workflow and column objects have been correctly obtained
    if column.position > 1:
        reposition_column_and_update_df(workflow, column, column.position - 1)

    return JsonResponse({})


@user_passes_test(is_instructor)
def column_move_next(request, pk):
    """

    :param request: HTTP request to move a column to its next position
    :param pk: Column ID
    :return:
    """

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse({'html_redirect': reverse('workflow:index')})

    # Get the column
    try:
        column = Column.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        return JsonResponse({
            'html_redirect': reverse('workflow:detail',
                                     kwargs={'pk': workflow.id})
        })

    # The workflow and column objects have been correctly obtained
    if column.position < workflow.ncols:
        reposition_column_and_update_df(workflow, column, column.position + 1)

    return JsonResponse({})


@user_passes_test(is_instructor)
def column_move_top(request, pk):
    """

    :param request: HTTP request to move a column to the top of the list
    :param pk: Column ID
    :return:
    """

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse({'html_redirect': reverse('workflow:index')})

    # Get the column
    try:
        column = Column.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        return JsonResponse({
            'html_redirect': reverse('workflow:detail',
                                     kwargs={'pk': workflow.id})
        })

    # The workflow and column objects have been correctly obtained
    if column.position > 1:
        reposition_column_and_update_df(workflow, column, 1)

    return JsonResponse({})


@user_passes_test(is_instructor)
def column_move_bottom(request, pk):
    """

    :param request: HTTP request to move a column to end of the list
    :param pk: Column ID
    :return:
    """

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        return JsonResponse({'html_redirect': reverse('workflow:index')})

    # Get the column
    try:
        column = Column.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        return JsonResponse({
            'html_redirect': reverse('workflow:detail',
                                     kwargs={'pk': workflow.id})
        })

    # The workflow and column objects have been correctly obtained
    if column.position < workflow.ncols:
        reposition_column_and_update_df(workflow, column, workflow.ncols)

    return JsonResponse({})


@user_passes_test(is_instructor)
def column_restrict_values(request, pk):
    """
    Restrict future values in this column to one of those already present.
    :param request: HTTP request
    :param pk: ID of the column to restrict. The workflow element is taken
     from the session.
    :return: Render the delete column form
    """

    # JSON response, context and default values
    data = dict()  # JSON response

    # Get the workflow element
    workflow = get_workflow(request)
    if not workflow:
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:index')
        return JsonResponse(data)

    data['form_is_valid'] = False
    context = {'pk': pk}  # For rendering

    # Get the column
    try:
        column = Column.objects.get(pk=pk, workflow=workflow)
    except ObjectDoesNotExist:
        # The column is not there. Redirect to workflow detail
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail',
                                        kwargs={'pk': workflow.id})
        return JsonResponse(data)

    # If the columns is unique and it is the only one, we cannot allow
    # the operation
    if column.is_key:
        # This is the only key column
        messages.error(request, _('You cannot restrict a key column'))
        data['form_is_valid'] = True
        data['html_redirect'] = reverse('workflow:detail',
                                        kwargs={'pk': workflow.id})
        return JsonResponse(data)

    # Get the name of the column to delete
    context['cname'] = column.name

    # Get the values from the data frame
    df = pandas_db.load_from_db(workflow.id)
    context['values'] = ', '.join(set(df[column.name]))

    if request.method == 'POST':
        # Proceed restricting the column
        result = workflow_restrict_column(workflow, column)

        if isinstance(result, str):
            # Something went wrong. Show it
            messages.error(request, result)

            # Log the event
            Log.objects.register(request.user,
                                 Log.COLUMN_RESTRICT,
                                 workflow,
                                 {'id': workflow.id,
                                  'name': workflow.name,
                                  'column_name': column.name,
                                  'values': context['values']})

        data['form_is_valid'] = True

        # There are various points of return
        from_url = request.META['HTTP_REFERER']
        if from_url.endswith(reverse('table:display')):
            data['html_redirect'] = reverse('table:display')
        else:
            data['html_redirect'] = reverse('workflow:detail',
                                            kwargs={'pk': workflow.id})
        return JsonResponse(data)

    data['html_form'] = render_to_string(
        'workflow/includes/partial_column_restrict.html',
        context,
        request=request)

    return JsonResponse(data)
