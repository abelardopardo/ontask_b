# -*- coding: utf-8 -*-

"""Views for create/rename/update/delete columns."""

from builtins import range
import random
from typing import Optional

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.http import HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ontask.core.decorators import ajax_required, get_column, get_workflow
from ontask.core.permissions import is_instructor
from ontask.dataops.formula import evaluation
from ontask.dataops.pandas import (
    load_table, pandas_datatype_names, rename_df_column, store_dataframe,
)
from ontask.dataops.sql import add_column_to_db, db_rename_column
from ontask.models import (
    ActionColumnConditionTuple, Column, Condition, Log, Workflow,
)
from ontask.workflow.forms import (
    ColumnAddForm, ColumnRenameForm, FormulaColumnAddForm, QuestionForm,
    RandomColumnAddForm,
)
from ontask.workflow.ops import clone_wf_column, workflow_delete_column

# These are the column operands offered through the GUI. They have immediate
# translations onto Pandas operators over dataframes.
# Each tuple has:
# - Pandas operation name
# - Textual description
# - List of data types that are allowed (for data type checking)
_formula_column_operands = [
    ('sum', _('sum: Sum selected columns'), ['integer', 'double']),
    (
        'prod',
        _('prod: Product of the selected columns'),
        ['integer', 'double']),
    ('max', _('max: Maximum of the selected columns'), ['integer', 'double']),
    ('min', _('min: Minimum of the selected columns'), ['integer', 'double']),
    ('mean', _('mean: Mean of the selected columns'), ['integer', 'double']),
    (
        'median',
        _('median: Median of the selected columns'),
        ['integer', 'double']),
    (
        'std',
        _('std: Standard deviation over the selected columns'),
        ['integer', 'double']),
    (
        'all',
        _('all: True when all elements in selected columns are true'),
        ['boolean']),
    (
        'any',
        _('any: True when any element in selected columns is true'),
        ['boolean']),
]

_op_distrib = {
    'sum': lambda operand: operand.sum(axis=1, skipna=False),
    'prod': lambda operand: operand.prod(axis=1, skipna=False),
    'max': lambda operand: operand.max(axis=1, skipna=False),
    'min': lambda operand: operand.min(axis=1, skipna=False),
    'mean': lambda operand: operand.mean(axis=1, skipna=False),
    'median': lambda operand: operand.median(axis=1, skipna=False),
    'std': lambda operand: operand.std(axis=1, skipna=False),
    'all': lambda operand: operand.all(axis=1, skipna=False),
    'any': lambda operand: operand.any(axis=1, skipna=False),
}


def _partition(list_in, num):
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
@ajax_required
@get_workflow(pf_related=['actions', 'columns'])
def column_add(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
    """Add a column.

    :param request: Http Request

    :param pk: Action ID where to add the question

    :return: JSON response
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
        form = QuestionForm(request.POST or None, workflow=workflow)
    else:
        form = ColumnAddForm(request.POST or None, workflow=workflow)

    if request.method == 'POST' and form.is_valid():
        # Processing now a valid POST request
        column_initial_value = form.initial_valid_value

        # Save the column object attached to the form
        column = form.save(commit=False)

        # Catch the special case of integer type and no initial value. Pandas
        # encodes it as NaN but a cycle through the database transforms it into
        # a string. To avoid this case, integer + empty value => double
        if column.data_type == 'integer' and column_initial_value is None:
            column.data_type = 'double'

        # Fill in the remaining fields in the column
        column.workflow = workflow
        column.is_key = False

        # Update the positions of the appropriate columns
        workflow.reposition_columns(workflow.ncols + 1, column.position)

        # Save column, refresh workflow, and increase number of columns
        column.save()
        form.save_m2m()
        workflow.refresh_from_db()
        workflow.ncols += 1
        workflow.set_query_builder_ops()
        workflow.save()

        # Add the new column to the DB
        try:
            add_column_to_db(
                workflow.get_data_frame_table_name(),
                column.name,
                column.data_type,
                initial=column_initial_value)
        except Exception as exc:
            messages.error(
                request,
                _('Unable to add column: {0}').format(str(exc)))
            return JsonResponse({'html_redirect': ''})

        # If the column is a question, add it to the action
        if is_question:
            acc = ActionColumnConditionTuple.objects.get_or_create(
                action=action,
                column=column,
                condition=None)

        context = {
            'column_name': column.name,
            'column_type': column.data_type}
        # Log the event
        if is_question:
            acc.log(request.user, Log.ACTION_QUESTION_ADD, context)
        else:
            column.log(request.user, Log.COLUMN_ADD)

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
@ajax_required
@get_workflow(pf_related='columns')
def formula_column_add(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
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
        operands=_formula_column_operands,
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
            df[column.name] = _op_distrib[operation](df[cnames])
        except Exception as exc:
            column.delete()

            # Notify in the form
            form.add_error(
                None,
                _('Unable to add the column: {0}').format(exc))
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
        column.save()
        workflow.refresh_from_db()

        # Store the df to DB
        try:
            store_dataframe(df, workflow)
        except Exception as exc:
            messages.error(
                request,
                _('Unable to clone column: {0}').format(str(exc)))
            column.delete()
            return JsonResponse({'html_redirect': ''})

        workflow.ncols = workflow.columns.count()
        workflow.save()
        column.log(request.user, Log.COLUMN_ADD_FORMULA)
        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_formula_column_add.html',
            {'form': form},
            request=request,
        ),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_workflow(pf_related='columns')
def random_column_add(
    request: HttpRequest,
    workflow: Optional[Workflow] = None,
) -> JsonResponse:
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
    form = RandomColumnAddForm(
        data=request.POST or None,
        workflow=workflow,
        allow_interval_as_initial=True)

    if request.method == 'POST' and form.is_valid():

        # Save the column object attached to the form and add additional fields
        column: Column = form.save(commit=False)
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

        # Detect the case of a single integer as initial value so that it is
        # expanded
        try:
            int_value: int = int(column.categories[0])
        except (ValueError, TypeError, IndexError):
            int_value: Optional[str] = None

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

            column.set_categories([idx + 1 for idx in range(int_value)])

        column.save()

        # Empty new column
        new_column = [None] * workflow.nrows
        # Create the random partitions
        partitions = _partition(
            [idx for idx in range(workflow.nrows)],
            len(column.categories))

        # Assign values to partitions
        for idx, indexes in enumerate(partitions):
            for col_idx in indexes:
                new_column[col_idx] = column.categories[idx]

        # Assign the new column to the data frame
        form.data_frame[column.name] = new_column

        # Update the positions of the appropriate columns
        workflow.reposition_columns(workflow.ncols + 1, column.position)
        workflow.refresh_from_db()

        # Store the df to DB
        try:
            store_dataframe(form.data_frame, workflow)
        except Exception as exc:
            messages.error(
                request,
                _('Unable to add the column: {0}').format(str(exc)))
            column.delete()
            return JsonResponse({'html_redirect': ''})

        workflow.ncols = workflow.columns.count()
        workflow.save()

        # Log the event
        column.log(request.user, Log.COLUMN_ADD_RANDOM)

        # The form has been successfully processed
        return JsonResponse({'html_redirect': ''})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_random_column_add.html',
            {'form': form},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_column(pf_related=['columns', 'views', 'actions'])
def column_edit(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    column: Optional[Column] = None,
) -> JsonResponse:
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
        form = QuestionForm(
            request.POST or None,
            workflow=workflow,
            instance=column)
    else:
        form = ColumnRenameForm(
            request.POST or None,
            workflow=workflow,
            instance=column)

    if request.method == 'POST' and form.is_valid():
        if not form.has_changed():
            return JsonResponse({'html_redirect': None})

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
            id=workflow.id,
        )

        # Changes in column require rebuilding the query_builder_ops
        workflow.set_query_builder_ops()

        # Save the workflow
        workflow.save()

        # Log the event
        column.log(request.user, Log.COLUMN_EDIT)

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
             'cname': column.name,
             'pk': pk},
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_column(pf_related=['columns', 'actions'])
def column_delete(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    column: Optional[Column] = None,
) -> JsonResponse:
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
        return JsonResponse({'html_redirect': reverse('workflow:detail')})

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
        column.log(request.user, Log.COLUMN_DELETE)
        workflow_delete_column(workflow, column, cond_to_delete)

        # There are various points of return
        from_url = request.META['HTTP_REFERER']
        if from_url.endswith(reverse('table:display')):
            return JsonResponse({'html_redirect': reverse('table:display')})

        return JsonResponse({'html_redirect': reverse('workflow:detail')})

    return JsonResponse({
        'html_form': render_to_string(
            'workflow/includes/partial_column_delete.html',
            context,
            request=request),
    })


@user_passes_test(is_instructor)
@ajax_required
@get_column(pf_related='columns')
def column_clone(
    request: HttpRequest,
    pk: int,
    workflow: Optional[Workflow] = None,
    column: Optional[Column] = None,
) -> JsonResponse:
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

    # Proceed to clone the column
    try:
        new_column = clone_wf_column(column)
    except Exception as exc:
        messages.error(
            request,
            _('Unable to clone column: {0}').format(str(exc)))
        return JsonResponse({'html_redirect': ''})

    column.log(request.user, Log.COLUMN_CLONE)
    return JsonResponse({'html_redirect': ''})
