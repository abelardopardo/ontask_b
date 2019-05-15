# -*- coding: utf-8 -*-

"""Views for create/rename/update/delete columns."""

import random
from builtins import range
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from action.models import ActionColumnConditionTuple, Condition
from dataops.formula import evaluation
from dataops.pandas import (
    add_column_to_df, load_table, pandas_datatype_names, rename_df_column,
    store_dataframe,
)
from dataops.sql import db_rename_column
from logs.models import Log
from ontask import create_new_name
from ontask.decorators import get_column, get_workflow
from ontask.permissions import is_instructor
from workflow.forms import (
    ColumnAddForm, ColumnRenameForm, FormulaColumnAddForm, QuestionAddForm,
    QuestionRenameForm, RandomColumnAddForm,
)
from workflow.models import Column, Workflow
from workflow.ops import clone_column, workflow_delete_column

# These are the column operands offered through the GUI. They have immediate
# translations onto Pandas operators over dataframes.
# Each tuple has:
# - Pandas operation name
# - Textual description
# - List of data types that are allowed (for data type checking)
formula_column_operands = [
    ('sum', _('sum: Sum selected columns'), ['integer', 'double']),
    ('prod',
     _('prod: Product of the selected columns'),
     ['integer', 'double']),
    ('max', _('max: Maximum of the selected columns'), ['integer', 'double']),
    ('min', _('min: Minimum of the selected columns'), ['integer', 'double']),
    ('mean', _('mean: Mean of the selected columns'), ['integer', 'double']),
    ('median',
     _('median: Median of the selected columns'),
     ['integer', 'double']),
    ('std',
     _('std: Standard deviation over the selected columns'),
     ['integer', 'double']),
    ('all',
     _('all: True when all elements in selected columns are true'),
     ['boolean']),
    ('any',
     _('any: True when any element in selected columns is true'),
     ['boolean']),
]


def partition(list_in, num):
    """Partitions the list in num lists.

    Given a list and n, returns a list with n lists, and inside each of them a
    set of elements from the shuffled list. All lists are of the same size

    :param list_in: List of elements to partition

    :param num: Number of partitions

    :return: List of lists with shuffled elements partitioned
    """
    random.shuffle(list_in)
    return [list_in[idx::num] for idx in range(num)]


@user_passes_test(is_instructor)
@get_workflow(pf_related=['actions', 'columns'])
def column_add(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Add column.

    :param request:

    :param pk:

    :return:
    """
    # Detect if this operation is to add a new column or a new question (in
    # the edit in page)
    is_question = pk is not None

    if workflow.nrows == 0:
        if is_question:
            messages.error(
                request,
                _('Cannot add question to a workflow without data'),
            )
        else:
            messages.error(
                request,
                _('Cannot add column to a workflow without data'),
            )
        return JsonResponse({'html_redirect': ''})

    action = None
    action_id = None
    if is_question:
        # Get the action and the columns
        action = workflow.actions.filter(pk=pk).first()
        action_id = action.id
        if not action:
            messages.error(
                request,
                _('Cannot find action to add question.'),
            )
            return JsonResponse({'html_redirect': reverse('action:index')})

    # Form to read/process data
    if is_question:
        form = QuestionAddForm(request.POST or None, workflow=workflow)
    else:
        form = ColumnAddForm(request.POST or None, workflow=workflow)

    if request.method == 'POST' and form.is_valid():
        # Processing now a valid POST request
        # Access the updated information
        column_initial_value = form.initial_valid_value

        # Save the column object attached to the form
        column = form.save(commit=False)

        # Catch the special case of integer type and no initial value. Pandas
        # encodes it as NaN but a cycle through the database transforms it into
        # a string. To avoid this case, integer + empty value => double
        if column.data_type == 'integer' and not column_initial_value:
            column.data_type = 'double'

        # Fill in the remaining fields in the column
        column.workflow = workflow
        column.is_key = False

        # Update the data frame, which must be stored in the form because
        # it was loaded when validating it.
        df = load_table(workflow.get_data_frame_table_name())

        # Add the column with the initial value to the dataframe
        df = add_column_to_df(df, column, column_initial_value)

        # Update the positions of the appropriate columns
        workflow.reposition_columns(workflow.ncols + 1, column.position)

        # Save column and clear prefetch queryset
        column.save()
        form.save_m2m()
        workflow = Workflow.objects.prefetch_related('columns').get(
            wid=workflow.id)

        # Store the df to DB
        store_dataframe(df, workflow)

        # If the column is a question, add it to the action
        if is_question:
            ActionColumnConditionTuple.objects.get_or_create(
                action=action,
                column=column,
                condition=None)

        # Log the event
        if is_question:
            event_type = Log.QUESTION_ADD
        else:
            event_type = Log.COLUMN_ADD
        Log.objects.register(
            request.user,
            event_type,
            workflow,
            {
                'id': workflow.id,
                'name': workflow.name,
                'column_name': column.name,
                'column_type': column.data_type})

        return JsonResponse({'html_redirect': ''})

    if is_question:
        template = 'workflow/includes/partial_question_addedit.html'
    else:
        template = 'workflow/includes/partial_column_addedit.html'

    return JsonResponse({
        'html_form': render_to_string(
            template,
            {
                'form': form,
                'is_question': is_question,
                'action_id': action_id,
                'add': True},
            request=request),
    })


@user_passes_test(is_instructor)
@get_workflow(pf_related='columns')
def formula_column_add(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Add a formula column.

    :param request:

    :return:
    """
    # Get the workflow element
    if workflow.nrows == 0:
        messages.error(
            request,
            _('Cannot add column to a workflow without data'),
        )
        return JsonResponse({'html_redirect': ''})

    # Form to read/process data
    form = FormulaColumnAddForm(
        form_data=request.POST or None,
        operands=formula_column_operands,
        columns=workflow.columns.all(),
    )

    if request.method == 'POST' and form.is_valid():
        # Save the column object attached to the form and add additional fields
        column = form.save(commit=False)
        column.workflow = workflow
        column.is_key = False

        # Save the instance
        try:
            column.save()
            form.save_m2m()
        except IntegrityError:
            form.add_error('name', _('A column with that name already exists'))
            return JsonResponse({
                'html_form': render_to_string(
                    'workflow/includes/partial_formula_column_add.html',
                    {'form': form},
                    request=request),
            })

        # Update the data frame
        df = load_table(workflow.get_data_frame_table_name())

        try:
            # Add the column with the appropriate computation
            operation = form.cleaned_data['op_type']
            cnames = [col.name for col in form.selected_columns]
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
                    _('Operand {0} not implemented').format(operation),
                )
        except Exception as exc:
            # Something went wrong in pandas, we need to remove the column
            column.delete()

            # Notify in the form
            form.add_error(
                None,
                _('Unable to perform the requested operation ({0})').format(
                    exc,
                ),
            )
            return JsonResponse({
                'html_form': render_to_string(
                    'workflow/includes/partial_formula_column_add.html',
                    {'form': form},
                    request=request,
                ),
            })

        # Populate the column type
        column.data_type = pandas_datatype_names.get(
            df[column.name].dtype.name)

        # Update the positions of the appropriate columns
        workflow.reposition_columns(workflow.ncols + 1, column.position)

        # Save column and refresh the prefetched related in the workflow
        column.save()
        workflow = Workflow.objects.prefetch_related('columns').get(
            wid=workflow.id)

        # Store the df to DB
        store_dataframe(df, workflow)

        # Log the event
        Log.objects.register(
            request.user,
            Log.COLUMN_ADD_FORMULA,
            workflow,
            {'id': workflow.id,
             'name': workflow.name,
             'column_name': column.name,
             'column_type': column.data_type})

        # The form has been successfully processed
        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_formula_column_add.html',
            {'form': form},
            request=request,
        ),
    })


@user_passes_test(is_instructor)
@get_workflow(pf_related='columns')
def random_column_add(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Create a column with random values (Modal).

    :param request:

    :return:
    """
    # Get the workflow element
    if workflow.nrows == 0:
        messages.error(
            request,
            _('Cannot add column to a workflow without data'))
        return JsonResponse({'html_redirect': ''})

    # Form to read/process data
    form = RandomColumnAddForm(data=request.POST or None)

    if request.method == 'POST' and form.is_valid():

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
            return JsonResponse({
                'html_form': render_to_string(
                    'workflow/includes/partial_random_column_add.html',
                    {'form': form},
                    request=request),
            })

        # Update the data frame
        df = load_table(workflow.get_data_frame_table_name())

        # Get the values and interpret its meaning
        column_values = form.cleaned_data['column_values']
        # First, try to see if the field is a valid integer
        try:
            int_value = int(column_values)
        except ValueError:
            int_value = None

        if int_value:
            # At this point the field is an integer
            if int_value <= 1:
                form.add_error(
                    'values',
                    _('The integer value has to be larger than 1'))
                return JsonResponse({
                    'html_form': render_to_string(
                        'workflow/includes/partial_random_column_add.html',
                        {'form': form},
                        request=request),
                })

            intvals = [idx + 1 for idx in range(int_value)]
        else:
            # At this point the field is a string and the values are the comma
            # separated strings.
            intvals = [
                valstr.strip() for valstr in column_values.strip().split(',')
                if valstr
            ]
            if not intvals:
                form.add_error(
                    'values',
                    _('The value has to be a comma-separated list'),
                )
                return JsonResponse({
                    'html_form': render_to_string(
                        'workflow/includes/partial_random_column_add.html',
                        {'form': form},
                        request=request),
                })

        # Empty new column
        new_column = [None] * workflow.nrows
        # Create the random partitions
        partitions = partition(
            [idx for idx in range(workflow.nrows)],
            len(intvals))

        # Assign values to partitions
        for idx, indexes in enumerate(partitions):
            for col_idx in indexes:
                new_column[col_idx] = intvals[idx]

        # Assign the new column to the data frame
        df[column.name] = new_column

        # Populate the column type
        column.data_type = pandas_datatype_names.get(
            df[column.name].dtype.name,
        )

        # Update the positions of the appropriate columns
        workflow.reposition_columns(workflow.ncols + 1, column.position)

        column.save()
        workflow = Workflow.objects.prefetch_related('columns').get(
            wid=workflow.id)

        # Store the df to DB
        store_dataframe(df, workflow)

        # Log the event
        Log.objects.register(
            request.user,
            Log.COLUMN_ADD_RANDOM,
            workflow,
            {'id': workflow.id,
             'name': workflow.name,
             'column_name': column.name,
             'column_type': column.data_type,
             'value': column_values})

        # The form has been successfully processed
        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_random_column_add.html',
            {'form': form},
            request=request),
    })


@user_passes_test(is_instructor)
@get_column(pf_related=['columns', 'views', 'actions'])
def column_edit(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    column: Optional[Column] = None,
) -> HttpResponse:
    """Edit a column.

    :param request:

    :param pk:

    :return:
    """
    # Detect if this operation is to edit a new column or a new question (in
    # the edit in page)
    is_question = 'question_edit' in request.path_info
    # Form to read/process data
    if is_question:
        form = QuestionRenameForm(
            request.POST or None,
            workflow=workflow,
            instance=column)
    else:
        form = ColumnRenameForm(
            request.POST or None,
            workflow=workflow,
            instance=column)

    if request.method == 'POST' and form.is_valid():
        # Process further only if any data changed.
        if form.changed_data:

            # Some field changed value, so save the result, but
            # no commit as we need to propagate the info to the df
            column = form.save(commit=False)

            # If there is a new name, rename the data frame columns
            if form.old_name != form.cleaned_data['name']:
                db_rename_column(
                    workflow.get_data_frame_table_name(),
                    form.old_name,
                    column.name)
                rename_df_column(workflow, form.old_name, column.name)

            if form.old_position != form.cleaned_data['position']:
                # Update the positions of the appropriate columns
                workflow.reposition_columns(form.old_position, column.position)

            # Save the column information
            column.save()

            # Go back to the DB because the prefetch columns are not valid
            # any more
            workflow = Workflow.objects.prefetch_related('columns').get(
                wid=workflow.id,
            )

            # Changes in column require rebuilding the query_builder_ops
            workflow.set_query_builder_ops()

            # Save the workflow
            workflow.save()

        # Log the event
        if is_question:
            event_type = Log.QUESTION_ADD
        else:
            event_type = Log.COLUMN_ADD
        Log.objects.register(
            request.user,
            event_type,
            workflow,
            {
                'id': workflow.id,
                'name': workflow.name,
                'column_name': form.old_name,
                'new_name': column.name})

        # Done processing the correct POST request
        return JsonResponse({'html_redirect': ''})

    if is_question:
        template = 'workflow/includes/partial_question_addedit.html'
    else:
        template = 'workflow/includes/partial_column_addedit.html'
    return JsonResponse({
        'html_form': render_to_string(
            template,
            {'form': form,
             'cname': form.old_name,
             'pk': pk},
            request=request),
    })


@user_passes_test(is_instructor)
@get_column(pf_related=['columns', 'actions'])
def column_delete(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    column: Optional[Column] = None,
) -> HttpResponse:
    """Delete a column in the table attached to a workflow.

    :param request: HTTP request

    :param pk: ID of the column to delete. The workflow element is taken
     from the session.

    :return: Render the delete column form
    """
    # Get the workflow element
    # If the columns is unique and it is the only one, we cannot allow
    # the operation
    unique_column = workflow.get_column_unique()
    if column.is_key and len([col for col in unique_column if col]) == 1:
        # This is the only key column
        messages.error(request, _('You cannot delete the only key column'))
        return JsonResponse({
            'html_redirect': reverse(
                'workflow:detail',
                kwargs={'pk': workflow.id}),
        })

    # Get the name of the column to delete
    context = {'pk': pk, 'cname': column.name}

    # Get the conditions/actions attached to this workflow
    cond_to_delete = [
        col for col in Condition.objects.filter(action__workflow=workflow)
        if evaluation.has_variable(col.formula, column.name)]
    # Put it in the context because it is shown to the user before confirming
    # the deletion
    context['cond_to_delete'] = cond_to_delete

    if request.method == 'POST':
        # Proceed deleting the column
        workflow_delete_column(workflow, column, cond_to_delete)

        # Log the event
        Log.objects.register(
            request.user,
            Log.COLUMN_DELETE,
            workflow,
            {
                'id': workflow.id,
                'name': workflow.name,
                'column_name': column.name})

        # There are various points of return
        from_url = request.META['HTTP_REFERER']
        if from_url.endswith(reverse('table:display')):
            return JsonResponse({'html_redirect': reverse('table:display')})

        return JsonResponse({
            'html_redirect': reverse(
                'workflow:detail',
                kwargs={'pk': workflow.id}),
        })

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_column_delete.html',
            context,
            request=request),
    })


@user_passes_test(is_instructor)
@get_column(pf_related='columns')
def column_clone(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    column: Optional[Column] = None,
) -> HttpResponse:
    """Clone a column in the table attached to a workflow.

    :param request: HTTP request

    :param pk: ID of the column to clone. The workflow element is taken
     from the session.

    :return: Render the clone column form
    """
    # Get the name of the column to clone
    context = {'pk': pk, 'cname': column.name}

    if request.method == 'GET':
        return JsonResponse({
            'html_form': render_to_string(
                'workflow/includes/partial_column_clone.html',
                context,
                request=request),
        })

    # POST REQUEST

    # Get the new name appending as many times as needed the 'Copy of '
    old_name = column.name

    # Proceed to clone the column
    column = clone_column(
        column,
        None,
        create_new_name(column.name, workflow.columns))

    # Log the event
    Log.objects.register(
        request.user,
        Log.COLUMN_CLONE,
        workflow,
        {
            'id': workflow.id,
            'name': workflow.name,
            'old_column_name': old_name,
            'new_column_name': column.name})

    return JsonResponse({'html_redirect': ''})
